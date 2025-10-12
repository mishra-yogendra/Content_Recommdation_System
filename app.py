# Enhanced Streamlit Frontend Application with Visual Book Display
import streamlit as st
import uuid
import json
from agent import chatbot_wrapper, retrieve_all_threads, get_thread_name
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import Dict, Any


# =========================== Enhanced Display Functions ===========================
def display_book_recommendations(books_data: Dict[str, Any]):
    """Display book recommendations with covers and details in Streamlit."""
    if "error" in books_data:
        st.error(f"❌ {books_data['error']}")
        return True

    books = books_data.get("books", [])
    genre = books_data.get("genre", "")

    if not books:
        st.warning(f"No books found for genre: {genre}")
        return True

    st.markdown(f"### 📚 Book Recommendations: {genre.title()}")
    st.markdown(f"*Found {len(books)} great books for you!*")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["🖼️ Grid View", "📝 Detailed View"])

    with tab1:
        # Grid view with book covers
        cols = st.columns(min(3, len(books)))
        for idx, book in enumerate(books):
            with cols[idx % 3]:
                # Book cover
                if book['thumbnail'] and book[
                    'thumbnail'] != 'https://via.placeholder.com/128x190/cccccc/666666?text=No+Cover':
                    try:
                        st.image(book['thumbnail'], width=150)
                    except:
                        st.image('https://via.placeholder.com/150x220/cccccc/666666?text=No+Cover', width=150)
                else:
                    st.image('https://via.placeholder.com/150x220/cccccc/666666?text=No+Cover', width=150)

                # Book details card
                st.markdown(f"**{book['title'][:40]}{'...' if len(book['title']) > 40 else ''}**")
                st.markdown(f"*{book['author_display'][:30]}{'...' if len(book['author_display']) > 30 else ''}*")

                # Rating
                if book.get('averageRating'):
                    stars = "⭐" * int(float(book['averageRating']))
                    st.markdown(f"{stars} ({book['averageRating']}/5)")

                # Quick info
                if book['publishedDate'] != 'Unknown':
                    st.markdown(f"📅 {book['publishedDate']}")
                if book['pageCount'] != 'Unknown':
                    st.markdown(f"📄 {book['pageCount']} pages")

                # Action buttons
                if book.get('previewLink'):
                    st.link_button("👀 Preview", book['previewLink'], key=f"preview_{idx}")

                st.divider()

    with tab2:
        # Detailed list view
        for idx, book in enumerate(books):
            with st.expander(f"{idx + 1}. {book['title']}", expanded=(idx == 0)):
                col1, col2 = st.columns([1, 3])

                with col1:
                    # Book cover
                    if book['thumbnail'] and book[
                        'thumbnail'] != 'https://via.placeholder.com/128x190/cccccc/666666?text=No+Cover':
                        try:
                            st.image(book['thumbnail'], width=120)
                        except:
                            st.image('https://via.placeholder.com/120x180/cccccc/666666?text=No+Cover', width=120)
                    else:
                        st.image('https://via.placeholder.com/120x180/cccccc/666666?text=No+Cover', width=120)

                with col2:
                    # Detailed information
                    st.markdown(f"**📝 Title:** {book['title']}")
                    st.markdown(f"**✍️ Author(s):** {book['author_display']}")

                    if book.get('publisher', 'Unknown Publisher') != 'Unknown Publisher':
                        st.markdown(f"**🏢 Publisher:** {book['publisher']}")

                    if book['publishedDate'] != 'Unknown':
                        st.markdown(f"**📅 Published:** {book['publishedDate']}")

                    if book['pageCount'] != 'Unknown':
                        st.markdown(f"**📄 Pages:** {book['pageCount']}")

                    if book.get('category_display'):
                        st.markdown(f"**🏷️ Categories:** {book['category_display']}")

                    if book.get('averageRating'):
                        stars = "⭐" * int(float(book['averageRating']))
                        st.markdown(f"**⭐ Rating:** {stars} {book['averageRating']}/5")
                        if book.get('ratingsCount', 0) > 0:
                            st.markdown(f"**👥 Reviews:** {book['ratingsCount']} reviews")

                # Description
                if book['description'] != 'No description available':
                    st.markdown("**📖 Description:**")
                    st.write(book['description'])

                # Action buttons
                button_cols = st.columns(3)

                with button_cols[0]:
                    if book.get('previewLink'):
                        st.link_button("📖 Read Preview", book['previewLink'],
                                       key=f"detailed_preview_{idx}", use_container_width=True)

                with button_cols[1]:
                    if book.get('infoLink'):
                        st.link_button("ℹ️ More Info", book['infoLink'],
                                       key=f"info_{idx}", use_container_width=True)

                with button_cols[2]:
                    # Search on Goodreads
                    goodreads_search = f"https://www.goodreads.com/search?q={book['title'].replace(' ', '+')}"
                    st.link_button("📚 Goodreads", goodreads_search,
                                   key=f"goodreads_{idx}", use_container_width=True)

    return True


def display_movie_recommendations(movies_data: Dict[str, Any]):
    """Display movie recommendations with posters and details."""
    if "error" in movies_data:
        st.error(f"❌ {movies_data['error']}")
        return True

    movies = movies_data.get("movies", [])
    genre = movies_data.get("genre", "")

    if not movies:
        st.warning(f"No movies found for genre: {genre}")
        return True

    st.markdown(f"### 🎬 Movie Recommendations: {genre.title()}")

    cols = st.columns(min(3, len(movies)))
    for idx, movie in enumerate(movies):
        with cols[idx % 3]:
            # Movie poster
            if movie.get('poster_path'):
                try:
                    st.image(movie['poster_path'], width=150)
                except:
                    st.image('https://via.placeholder.com/150x225/cccccc/666666?text=No+Poster', width=150)
            else:
                st.image('https://via.placeholder.com/150x225/cccccc/666666?text=No+Poster', width=150)

            st.markdown(f"**{movie['title']}**")
            st.markdown(f"⭐ {movie.get('rating', 'N/A')}/10")
            st.markdown(f"📅 {movie.get('release_date', 'Unknown')}")

            with st.expander("Read More"):
                st.write(movie.get('overview', 'No overview available'))

    return True


def display_song_recommendations(songs_data: Dict[str, Any]):
    """Display song recommendations with album covers."""
    if "error" in songs_data:
        st.error(f"❌ {songs_data['error']}")
        return True

    songs = songs_data.get("songs", [])
    genre = songs_data.get("genre", "")

    if not songs:
        st.warning(f"No songs found for genre: {genre}")
        return True

    st.markdown(f"### 🎵 Song Recommendations: {genre.title()}")

    for idx, song in enumerate(songs):
        col1, col2 = st.columns([1, 4])

        with col1:
            if song.get('image_url'):
                try:
                    st.image(song['image_url'], width=80)
                except:
                    st.image('https://via.placeholder.com/80x80/cccccc/666666?text=♪', width=80)
            else:
                st.image('https://via.placeholder.com/80x80/cccccc/666666?text=♪', width=80)

        with col2:
            st.markdown(f"**{song['name']}**")
            st.markdown(f"*by {', '.join(song.get('artists', ['Unknown']))}*")
            st.markdown(f"Album: {song.get('album', 'Unknown')}")

            if song.get('external_url'):
                st.link_button("🎧 Listen on Spotify", song['external_url'], key=f"spotify_{idx}")

        st.divider()

    return True


def display_youtube_recommendations(videos_data: Dict[str, Any]):
    """Display YouTube video recommendations with thumbnails."""
    if "error" in videos_data:
        st.error(f"❌ {videos_data['error']}")
        return True

    videos = videos_data.get("videos", [])
    topic = videos_data.get("topic", "")

    if not videos:
        st.warning(f"No videos found for topic: {topic}")
        return True

    st.markdown(f"### 📺 YouTube Videos: {topic.title()}")

    for idx, video in enumerate(videos):
        col1, col2 = st.columns([1, 3])

        with col1:
            if video.get('thumbnail'):
                try:
                    st.image(video['thumbnail'], width=120)
                except:
                    st.image('https://via.placeholder.com/120x90/cccccc/666666?text=Video', width=120)
            else:
                st.image('https://via.placeholder.com/120x90/cccccc/666666?text=Video', width=120)

        with col2:
            st.markdown(f"**{video['title']}**")
            st.markdown(f"*by {video.get('channel', 'Unknown Channel')}*")
            st.write(video.get('description', 'No description')[:100] + "...")

            if video.get('url'):
                st.link_button("📺 Watch Video", video['url'], key=f"youtube_{idx}")

        st.divider()

    return True


def check_and_display_recommendations(content: str, messages: list):
    """Check if the response contains recommendations and display them visually."""
    # Look for tool calls in recent messages
    for msg in reversed(messages[-5:]):  # Check last 5 messages
        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get('name', '')

                # Find corresponding tool message
                for tool_msg in reversed(messages[-10:]):
                    if isinstance(tool_msg, ToolMessage) and tool_msg.tool_call_id == tool_call['id']:
                        try:
                            tool_result = json.loads(tool_msg.content) if isinstance(tool_msg.content,
                                                                                     str) else tool_msg.content

                            if tool_name == 'get_book_recommendations':
                                if display_book_recommendations(tool_result):
                                    return True
                            elif tool_name == 'get_movie_recommendations':
                                if display_movie_recommendations(tool_result):
                                    return True
                            elif tool_name == 'get_song_recommendations':
                                if display_song_recommendations(tool_result):
                                    return True
                            elif tool_name == 'get_youtube_videos':
                                if display_youtube_recommendations(tool_result):
                                    return True
                        except:
                            continue

    return False


# =========================== Utilities ===========================
def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []
    st.session_state["quiz_completed"] = False
    st.rerun()


def add_thread(thread_id):
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot_wrapper.get_state(thread_id)
    return state.get("messages", [])


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "quiz_completed" not in st.session_state:
    st.session_state["quiz_completed"] = False

# Ensure current thread is in the list
add_thread(st.session_state["thread_id"])

# ============================ Main UI ============================
st.set_page_config(
    page_title="AI Content Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 AI Content Recommender")
st.markdown("*Discover books, movies, songs, and more tailored just for you!*")

# ============================ Sidebar ============================
with st.sidebar:
    st.title("💬 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.divider()

    # Conversation history
    st.subheader("Recent Conversations")
    if st.session_state.get("chat_threads"):
        for thread_id in st.session_state["chat_threads"][:10]:
            thread_name = get_thread_name(thread_id)
            if st.button(
                    thread_name,
                    key=f"thread_{thread_id}",
                    use_container_width=True,
                    help=f"Thread ID: {thread_id[:8]}..."
            ):
                st.session_state["thread_id"] = thread_id
                messages = load_conversation(thread_id)

                temp_messages = []
                for msg in messages:
                    if isinstance(msg, HumanMessage):
                        temp_messages.append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        temp_messages.append({"role": "assistant", "content": msg.content})

                st.session_state["message_history"] = temp_messages
                state = chatbot_wrapper.get_state(thread_id)
                st.session_state["quiz_completed"] = state.get("quiz_completed", False)
                st.rerun()
    else:
        st.info("No conversations yet. Start chatting!")

    st.divider()

    # Quiz status indicator
    if st.session_state.get("quiz_completed", False):
        st.success("✅ Interest Quiz Completed")
        st.info("You can now get personalized recommendations!")
    else:
        st.warning("📝 Complete the interest quiz first")

# Main chat interface
st.subheader(f"Chat - {get_thread_name(st.session_state['thread_id'])}")

# Chat display
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Try to display recommendations first
            state = chatbot_wrapper.get_state(st.session_state["thread_id"])
            messages = state.get("messages", [])

            if not check_and_display_recommendations(message["content"], messages):
                st.markdown(message["content"])
        else:
            st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = chatbot_wrapper.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    st.session_state["thread_id"]
                )

                messages = result.get("messages", [])
                assistant_message = None
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        assistant_message = msg
                        break

                if assistant_message:
                    # Check for and display recommendations
                    if not check_and_display_recommendations(assistant_message.content, messages):
                        st.markdown(assistant_message.content)

                    # Add to history
                    st.session_state["message_history"].append(
                        {"role": "assistant", "content": assistant_message.content}
                    )

                    # Check quiz completion
                    quiz_indicators = [
                        "quiz completed", "quiz complete", "recommendations",
                        "now i can recommend", "based on your interests"
                    ]
                    if any(indicator in assistant_message.content.lower() for indicator in quiz_indicators):
                        st.session_state["quiz_completed"] = True
                        state = chatbot_wrapper.get_state(st.session_state["thread_id"])
                        state["quiz_completed"] = True
                        chatbot_wrapper.checkpointer.update_state(st.session_state["thread_id"], state)
                        st.rerun()

                else:
                    st.error("Sorry, I couldn't generate a response.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
