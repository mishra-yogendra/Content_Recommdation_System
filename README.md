# 🎯 AI Content Recommendation Agent

A sophisticated AI-powered content recommendation system that provides personalized suggestions for books, movies, songs, blogs, and YouTube videos based on user interests.

## 🌟 Features

### 🤖 Intelligent AI Agent
- **Conversational Interface**: Natural language interactions with users
- **Interest Quiz**: Adaptive quiz to understand user preferences
- **Personalized Recommendations**: Tailored content suggestions based on interests
- **Multi-modal Content**: Support for various content types (books, movies, music, etc.)

### 📚 Content Types Supported
- **Books**: Detailed recommendations with covers, ratings, and descriptions
- **Movies**: Popular films with posters and ratings
- **Music**: Song recommendations with album art and Spotify links
- **YouTube Videos**: Relevant video content with thumbnails
- **Blogs**: Curated articles and blog posts

### 💾 State Management
- **Conversation Persistence**: SQLite database for storing chat history
- **Session Management**: Multi-threaded conversation support
- **Checkpoint System**: Automatic state saving and recovery

### 🎨 User Interface
- **Streamlit Frontend**: Beautiful, responsive web interface
- **Visual Displays**: Book covers, movie posters, and album art
- **Grid & List Views**: Multiple display options for recommendations
- **Chat History**: Browse and resume previous conversations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API Key (for Gemini AI)
- Optional: API keys for content services

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mishra-yogendra/Content_Recommdation_System
cd ai-content-recommender
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file with your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_BOOKS_API_KEY=your_google_books_key
TMDB_API_KEY=your_tmdb_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
YOUTUBE_API_KEY=your_youtube_key
```

4. **Run the application**
```bash
streamlit run books.py
```

## 🛠️ Project Structure

```
ai-content-recommender/
├── agent.py              # Main AI agent with LangGraph workflow
├── books.py              # Streamlit frontend application
├── tools.py              # Content recommendation tools
├── task.py               # Background tasks and utilities
├── requirements.txt      # Python dependencies
└── chatbot.db           # SQLite database (created automatically)
```

## 📋 Core Components

### 🤖 AI Agent (`agent.py`)
- **LangGraph State Machine**: Manages conversation flow
- **Tool Integration**: Connects to various content APIs
- **Memory Management**: Handles user state and preferences
- **Quiz System**: Interactive interest assessment

### 🎨 Frontend (`books.py`)
- **Streamlit Interface**: Web-based chat interface
- **Visual Components**: Rich media displays for recommendations
- **Conversation Management**: Thread-based chat history
- **Responsive Design**: Mobile-friendly layout

### 🔧 Tools (`tools.py`)
- **Book Recommendations**: Google Books API integration
- **Movie Suggestions**: The Movie Database (TMDB) API
- **Music Discovery**: Spotify API integration
- **Video Content**: YouTube Data API
- **Blog Search**: Web search capabilities

### ⚙️ Utilities (`task.py`)
- **Data Export**: Conversation history export
- **Cleanup Tasks**: Database maintenance
- **Analytics**: Usage statistics and reports

## 🔌 API Integrations

The system integrates with multiple content providers:

| Service | Purpose | Required API Key |
|---------|---------|------------------|
| Google Gemini | AI Conversations | ✅ Required |
| Google Books | Book Recommendations | ✅ Required |
| The Movie Database | Movie Recommendations | ✅ Required |
| Spotify | Music Recommendations | ✅ Required |
| YouTube Data API | Video Recommendations | ✅ Required |
| DuckDuckGo | General Search | ❌ Optional |

## 💬 Usage Example

1. **Start a new chat** and complete the interest quiz
2. **Answer questions** about your preferences in books, movies, music, etc.
3. **Receive personalized recommendations** with rich visual displays
4. **Explore different content types** through natural conversation
5. **Save and resume conversations** using the chat history sidebar

## 🎯 Example Interaction

```
User: I love science fiction books and movies

AI: Great! Let me ask you a few questions to understand your preferences better...
[Interest quiz questions]

AI: Based on your interests, here are some recommendations:

📚 Books: "Dune" by Frank Herbert, "Foundation" by Isaac Asimov
🎬 Movies: "Blade Runner 2049", "Arrival"
🎵 Music: Sci-Fi inspired synthwave tracks
```

## 🔧 Configuration

### Environment Variables
All API keys are configured via environment variables in `.env`:

- `GOOGLE_API_KEY`: For Gemini AI model
- `GOOGLE_BOOKS_API_KEY`: For book recommendations
- `TMDB_API_KEY`: For movie database
- `SPOTIFY_CLIENT_ID` & `SPOTIFY_CLIENT_SECRET`: For music
- `YOUTUBE_API_KEY`: For video content

### Customization
- Modify `tools.py` to add new content sources
- Update `agent.py` to change conversation flow
- Customize display functions in `books.py` for different UI layouts

## 🚀 Deployment

### Local Development
```bash
streamlit run books.py
```

### Production Deployment
The application can be deployed on:
- **Streamlit Cloud**
- **Heroku** (with proper configuration)
- **AWS/Azure** with containerization
- **Docker** (create a Dockerfile for containerization)

## 📊 Features in Detail

### Intelligent Quiz System
- Adaptive questioning based on user responses
- Interest categorization and profiling
- Progressive refinement of recommendations

### Multi-format Display
- **Grid View**: Visual browsing with images
- **Detailed View**: Comprehensive information
- **Compact Mode**: Quick scanning of recommendations

### Advanced State Management
- SQLite-based conversation storage
- Thread-based isolation
- Automatic checkpointing and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the existing issues
- Create a new issue with detailed description
- Provide relevant logs and environment information

## 🎉 Acknowledgments

- **LangChain/LangGraph** for the AI agent framework
- **Streamlit** for the web interface
- **Google Gemini** for the AI model
- All content API providers (Google Books, TMDB, Spotify, YouTube)

---

**Note**: Ensure you have proper API keys and comply with the terms of service for all integrated platforms.
