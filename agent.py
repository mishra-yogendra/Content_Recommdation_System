# Content Recommendation Agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import sqlite3
import os
import json
from datetime import datetime
from tools import get_all_tools

load_dotenv()

# LLM Configuration
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_output_tokens=2048,
)

# Bind tools to LLM
tools = get_all_tools()
llm_with_tools = llm.bind_tools(tools)


# Custom reducer functions
def add_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]:
    """Reducer function for messages"""
    return left + right


def add_interests(left: List[str], right: List[str]) -> List[str]:
    """Reducer function for user interests"""
    return list(set(left + right))  # Remove duplicates


def update_quiz_status(left: bool, right: bool) -> bool:
    """Reducer function for quiz status"""
    return right  # Always take the latest value


# State Definition
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_interests: Annotated[List[str], add_interests]
    quiz_completed: Annotated[bool, update_quiz_status]


# Nodes
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]

    # Add system message based on whether quiz is completed
    if state.get("quiz_completed", False):
        system_message = SystemMessage(content="""You are a content recommendation assistant. 
        The user has completed their interest quiz. Provide personalized recommendations 
        for books, movies, songs, blogs, and YouTube videos based on their interests.
        When providing recommendations, include visual elements like covers/posters when available.
        Be engaging and helpful. Use the available tools to get specific recommendations.""")
    else:
        system_message = SystemMessage(content="""You are a content recommendation assistant. 
        Start by conducting an interest quiz to understand the user's preferences.
        Ask about 5 questions to determine their interests in various content types.
        After completing the quiz, provide personalized recommendations using the available tools.
        Mark quiz as completed when you have gathered sufficient information about user preferences.""")

    messages_with_system = [system_message] + messages
    response = llm_with_tools.invoke(messages_with_system)
    return {"messages": [response]}


# Create tool node
tool_node = ToolNode(tools)


# Graph Construction
def create_agent():
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge('tools', 'chat_node')

    return graph.compile()


# Create the agent
chatbot = create_agent()


# Custom SQLite Checkpointer
class SQLiteCheckpointer:
    def __init__(self, db_path="chatbot.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT PRIMARY KEY,
                state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_state(self, thread_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT state FROM checkpoints WHERE thread_id = ?", (thread_id,))
        result = cursor.fetchone()
        if result:
            state_data = json.loads(result[0])
            # Convert message dictionaries back to message objects
            messages = []
            for msg_data in state_data.get("messages", []):
                if msg_data.get("type") == "human":
                    messages.append(HumanMessage(content=msg_data["content"]))
                elif msg_data.get("type") == "ai":
                    messages.append(AIMessage(content=msg_data["content"]))
                elif msg_data.get("type") == "system":
                    messages.append(SystemMessage(content=msg_data["content"]))

            state_data["messages"] = messages
            return state_data
        return {"messages": [], "quiz_completed": False, "user_interests": []}

    def update_state(self, thread_id, state):
        cursor = self.conn.cursor()

        # Convert message objects to serializable dictionaries
        serializable_state = state.copy()
        messages_data = []
        for msg in state.get("messages", []):
            if isinstance(msg, HumanMessage):
                messages_data.append({"type": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages_data.append({"type": "ai", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                messages_data.append({"type": "system", "content": msg.content})

        serializable_state["messages"] = messages_data

        cursor.execute(
            "INSERT OR REPLACE INTO checkpoints (thread_id, state, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (thread_id, json.dumps(serializable_state))
        )
        self.conn.commit()

    def list_threads(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT thread_id FROM checkpoints ORDER BY updated_at DESC")
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()


# Initialize checkpointer
checkpointer = SQLiteCheckpointer()


# Helper Functions
def retrieve_all_threads():
    return checkpointer.list_threads()


def get_thread_name(thread_id):
    """Generate a name for a thread based on its content"""
    try:
        state = checkpointer.get_state(thread_id)
        messages = state.get("messages", [])

        # Find the first user message to use as thread name
        for msg in messages:
            if isinstance(msg, HumanMessage):
                # Truncate long messages
                content = msg.content
                if len(content) > 30:
                    content = content[:27] + "..."
                return f"Chat: {content}"

        return f"Thread {thread_id[:8]}..."
    except:
        return f"Thread {thread_id[:8]}..."


# Custom invoke function to handle state management
def chatbot_invoke(inputs, thread_id):
    # Get current state
    state = checkpointer.get_state(thread_id)

    # Update state with new inputs
    if "messages" in inputs:
        state["messages"].extend(inputs["messages"])

    # Run the graph
    result = chatbot.invoke(state)

    # Update state with result
    state.update(result)

    # Save updated state
    checkpointer.update_state(thread_id, state)

    return state


# For compatibility with existing code
chatbot_wrapper = type('ChatbotWrapper', (object,), {
    'invoke': chatbot_invoke,
    'get_state': checkpointer.get_state,
    'checkpointer': checkpointer
})