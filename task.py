# Background tasks for the content recommendation system
import sqlite3
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


def cleanup_old_conversations(days=30, db_path="chatbot.db"):
    """Remove conversations older than the specified number of days"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

        # Delete old conversations
        cursor.execute("DELETE FROM checkpoints WHERE created_at < ?", (cutoff_timestamp,))
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()

        return f"Cleaned up {deleted_count} conversations older than {days} days"
    except Exception as e:
        return f"Error during cleanup: {str(e)}"


def export_conversation_data(thread_id, filepath, db_path="chatbot.db"):
    """Export conversation data to a file"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT state FROM checkpoints WHERE thread_id = ?", (thread_id,))
        result = cursor.fetchone()

        if not result:
            return f"No conversation found for thread {thread_id}"

        state_data = json.loads(result[0])
        messages = state_data.get("messages", [])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Conversation Export for Thread: {thread_id}\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")

            for msg_data in messages:
                msg_type = msg_data.get("type", "unknown")
                content = msg_data.get("content", "")

                if msg_type == "human":
                    role = "User"
                elif msg_type == "ai":
                    role = "Assistant"
                elif msg_type == "system":
                    role = "System"
                else:
                    role = "Unknown"

                f.write(f"{role}: {content}\n\n")

            # Add metadata
            f.write("\n" + "=" * 50 + "\n")
            f.write("Conversation Metadata:\n")
            f.write(f"Quiz Completed: {state_data.get('quiz_completed', False)}\n")
            f.write(f"User Interests: {', '.join(state_data.get('user_interests', []))}\n")

        conn.close()
        return f"Conversation exported to {filepath}"
    except Exception as e:
        return f"Error exporting conversation: {str(e)}"


def generate_conversation_report(thread_id, db_path="chatbot.db"):
    """Generate a report of the conversation"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT state, created_at, updated_at FROM checkpoints WHERE thread_id = ?", (thread_id,))
        result = cursor.fetchone()

        if not result:
            return {"error": f"No conversation found for thread {thread_id}"}

        state_data = json.loads(result[0])
        messages = state_data.get("messages", [])

        user_msgs = [msg for msg in messages if msg.get("type") == "human"]
        assistant_msgs = [msg for msg in messages if msg.get("type") == "ai"]

        # Calculate conversation duration
        created_at = datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S')
        updated_at = datetime.strptime(result[2], '%Y-%m-%d %H:%M:%S')
        duration = updated_at - created_at

        report = {
            "thread_id": thread_id,
            "total_messages": len(messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "first_message": user_msgs[0].get("content", "") if user_msgs else None,
            "last_message": messages[-1].get("content", "") if messages else None,
            "quiz_completed": state_data.get("quiz_completed", False),
            "user_interests": state_data.get("user_interests", []),
            "created_at": result[1],
            "updated_at": result[2],
            "conversation_duration": str(duration),
            "average_message_length": sum(len(msg.get("content", "")) for msg in messages) / len(
                messages) if messages else 0
        }

        conn.close()
        return report
    except Exception as e:
        return {"error": str(e)}


def get_conversation_stats(db_path="chatbot.db"):
    """Get overall statistics about all conversations"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get total conversations
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        total_conversations = cursor.fetchone()[0]

        # Get conversations with completed quizzes
        cursor.execute("SELECT state FROM checkpoints")
        results = cursor.fetchall()

        completed_quizzes = 0
        total_messages = 0
        total_interests = set()

        for result in results:
            state_data = json.loads(result[0])
            if state_data.get("quiz_completed", False):
                completed_quizzes += 1
            total_messages += len(state_data.get("messages", []))
            total_interests.update(state_data.get("user_interests", []))

        stats = {
            "total_conversations": total_conversations,
            "completed_quizzes": completed_quizzes,
            "quiz_completion_rate": (completed_quizzes / total_conversations * 100) if total_conversations > 0 else 0,
            "total_messages": total_messages,
            "average_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0,
            "unique_interests": len(total_interests),
            "most_common_interests": list(total_interests)[:10]  # Top 10
        }

        conn.close()
        return stats
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    print("Running conversation statistics...")
    stats = get_conversation_stats()
    print(json.dumps(stats, indent=2))