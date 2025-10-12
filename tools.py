# Content Recommendation Tools
import os
import requests
from typing import Dict, Any
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import json

load_dotenv()

# Search tool for general queries
search_tool = DuckDuckGoSearchRun()


def safe_api_request(url: str, headers: dict = None, params: dict = None) -> dict:
    """Safely make API requests with error handling"""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON response: {str(e)}"}


@tool
def get_book_recommendations(genre: str, max_results: int = 5) -> Dict[str, Any]:
    """Get book recommendations by genre from Google Books API with enhanced visual data."""
    try:
        api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
        if not api_key:
            return {"error": "Google Books API key not configured"}

        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": f"subject:{genre}",
            "maxResults": min(max_results, 10),
            "key": api_key,
            "orderBy": "relevance"
        }

        data = safe_api_request(url, params=params)
        if "error" in data:
            return data

        books = []
        for item in data.get('items', [])[:max_results]:
            volume_info = item.get('volumeInfo', {})
            image_links = volume_info.get('imageLinks', {})

            # Get the best available image (prefer larger sizes)
            thumbnail = (
                    image_links.get('large') or
                    image_links.get('medium') or
                    image_links.get('small') or
                    image_links.get('thumbnail') or
                    image_links.get('smallThumbnail') or
                    'https://via.placeholder.com/128x190/cccccc/666666?text=No+Cover'
            )

            # Format description
            description = volume_info.get('description', '')
            if description:
                # Clean HTML tags if present
                import re
                description = re.sub('<.*?>', '', description)
                description = description[:300] + "..." if len(description) > 300 else description
            else:
                description = 'No description available'

            # Format authors
            authors = volume_info.get('authors', [])
            author_str = ', '.join(authors) if authors else 'Unknown Author'

            # Format rating
            average_rating = volume_info.get('averageRating')
            ratings_count = volume_info.get('ratingsCount', 0)
            rating_display = f"{average_rating}/5 ({ratings_count} reviews)" if average_rating else "Not rated"

            # Get categories/genres
            categories = volume_info.get('categories', [])
            category_str = ', '.join(categories[:3]) if categories else genre

            books.append({
                'title': volume_info.get('title', 'Unknown Title'),
                'authors': authors,
                'author_display': author_str,
                'description': description,
                'thumbnail': thumbnail,
                'previewLink': volume_info.get('previewLink', ''),
                'infoLink': volume_info.get('infoLink', ''),
                'publishedDate': volume_info.get('publishedDate', 'Unknown'),
                'pageCount': volume_info.get('pageCount', 'Unknown'),
                'averageRating': average_rating,
                'ratingsCount': ratings_count,
                'rating_display': rating_display,
                'categories': categories,
                'category_display': category_str,
                'language': volume_info.get('language', 'Unknown'),
                'publisher': volume_info.get('publisher', 'Unknown Publisher'),
                'isbn': next((identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', [])
                              if identifier['type'] in ['ISBN_13', 'ISBN_10']), 'Unknown'),
                'buyLink': item.get('saleInfo', {}).get('buyLink', ''),
                'price': item.get('saleInfo', {}).get('listPrice', {}).get('amount', 'Not available'),
                'currency': item.get('saleInfo', {}).get('listPrice', {}).get('currencyCode', ''),
                'availability': item.get('saleInfo', {}).get('saleability', 'Unknown')
            })

        return {
            "books": books,
            "genre": genre,
            "count": len(books),
            "display_type": "book_recommendations"  # Flag for UI to know how to display
        }
    except Exception as e:
        return {"error": f"Unexpected error in book recommendations: {str(e)}"}


def display_book_recommendations(books_data: Dict[str, Any], st):
    """Display book recommendations with covers and details in Streamlit."""
    if "error" in books_data:
        st.error(f"❌ {books_data['error']}")
        return

    books = books_data.get("books", [])
    genre = books_data.get("genre", "")

    if not books:
        st.warning(f"No books found for genre: {genre}")
        return

    st.markdown(f"### 📚 Book Recommendations: {genre.title()}")
    st.markdown(f"*Found {len(books)} great books for you!*")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["🖼️ Grid View", "📝 List View"])

    with tab1:
        # Grid view with book covers
        cols = st.columns(min(3, len(books)))
        for idx, book in enumerate(books):
            with cols[idx % 3]:
                # Book cover
                if book['thumbnail']:
                    try:
                        st.image(book['thumbnail'], width=150, caption=book['title'])
                    except:
                        st.image('https://via.placeholder.com/150x220/cccccc/666666?text=No+Cover',
                                 width=150, caption=book['title'])

                # Book details card
                with st.container():
                    st.markdown(f"**{book['title']}**")
                    st.markdown(f"*by {book['author_display']}*")

                    # Rating
                    if book['averageRating']:
                        stars = "⭐" * int(book['averageRating'])
                        st.markdown(f"{stars} {book['rating_display']}")

                    # Quick info
                    st.markdown(f"📅 {book['publishedDate']}")
                    if book['pageCount'] != 'Unknown':
                        st.markdown(f"📄 {book['pageCount']} pages")

                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if book['previewLink']:
                            st.link_button("👀 Preview", book['previewLink'])
                    with col2:
                        if book['infoLink']:
                            st.link_button("ℹ️ Info", book['infoLink'])

                st.divider()

    with tab2:
        # List view with detailed information
        for idx, book in enumerate(books, 1):
            with st.expander(f"{idx}. {book['title']} - {book['author_display']}", expanded=idx == 1):
                col1, col2 = st.columns([1, 2])

                with col1:
                    # Book cover
                    if book['thumbnail']:
                        try:
                            st.image(book['thumbnail'], width=120)
                        except:
                            st.image('https://via.placeholder.com/120x180/cccccc/666666?text=No+Cover', width=120)

                with col2:
                    # Detailed information
                    st.markdown(f"**Author(s):** {book['author_display']}")
                    st.markdown(f"**Publisher:** {book['publisher']}")
                    st.markdown(f"**Published:** {book['publishedDate']}")
                    st.markdown(f"**Pages:** {book['pageCount']}")
                    st.markdown(f"**Categories:** {book['category_display']}")
                    st.markdown(f"**Language:** {book['language']}")

                    if book['averageRating']:
                        stars = "⭐" * int(book['averageRating'])
                        st.markdown(f"**Rating:** {stars} {book['rating_display']}")

                    if book['isbn'] != 'Unknown':
                        st.markdown(f"**ISBN:** {book['isbn']}")

                # Description
                st.markdown("**Description:**")
                st.write(book['description'])

                # Action buttons
                button_cols = st.columns(4)
                with button_cols[0]:
                    if book['previewLink']:
                        st.link_button("📖 Preview", book['previewLink'], use_container_width=True)

                with button_cols[1]:
                    if book['infoLink']:
                        st.link_button("ℹ️ More Info", book['infoLink'], use_container_width=True)

                with button_cols[2]:
                    if book['buyLink']:
                        st.link_button("🛒 Buy", book['buyLink'], use_container_width=True)

                with button_cols[3]:
                    # Search on Goodreads
                    goodreads_search = f"https://www.goodreads.com/search?q={book['title'].replace(' ', '+')}"
                    st.link_button("📚 Goodreads", goodreads_search, use_container_width=True)


def display_book_grid_compact(books: list, st):
    """Compact grid display for quick browsing."""
    if not books:
        return

    st.markdown("#### Quick Browse")

    # Create a grid with more columns for compact view
    cols = st.columns(5)
    for idx, book in enumerate(books[:10]):  # Show max 10 in compact view
        with cols[idx % 5]:
            if book['thumbnail']:
                try:
                    st.image(book['thumbnail'], width=80)
                except:
                    st.image('https://via.placeholder.com/80x120/cccccc/666666?text=Book', width=80)

            st.markdown(f"**{book['title'][:30]}{'...' if len(book['title']) > 30 else ''}**",
                        help=f"by {book['author_display']}")

            if book['averageRating']:
                st.markdown(f"⭐ {book['averageRating']}")

            if book['previewLink']:
                st.link_button("Preview", book['previewLink'], key=f"compact_{idx}")

@tool
def get_movie_recommendations(genre: str, max_results: int = 5) -> Dict[str, Any]:
    """Get movie recommendations by genre from The Movie Database API."""
    try:
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            return {"error": "TMDB API key not configured"}

        # First get genre ID
        genre_url = f"https://api.themoviedb.org/3/genre/movie/list"
        genre_params = {"api_key": api_key}
        genre_data = safe_api_request(genre_url, params=genre_params)

        if "error" in genre_data:
            return genre_data

        genre_id = None
        for g in genre_data.get('genres', []):
            if g['name'].lower() == genre.lower():
                genre_id = g['id']
                break

        if not genre_id:
            # Fallback: search by keyword if exact genre not found
            movies_url = f"https://api.themoviedb.org/3/search/movie"
            movies_params = {
                "api_key": api_key,
                "query": genre,
                "sort_by": "popularity.desc",
                "page": 1
            }
        else:
            # Get movies by genre
            movies_url = f"https://api.themoviedb.org/3/discover/movie"
            movies_params = {
                "api_key": api_key,
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }

        movies_data = safe_api_request(movies_url, params=movies_params)
        if "error" in movies_data:
            return movies_data

        movies = []
        for movie in movies_data.get('results', [])[:max_results]:
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''

            movies.append({
                'title': movie.get('title', 'Unknown'),
                'overview': movie.get('overview', 'No overview available')[:200] + "..." if movie.get('overview',
                                                                                                      '') else 'No overview available',
                'poster_path': poster_url,
                'release_date': movie.get('release_date', 'Unknown'),
                'rating': movie.get('vote_average', 0),
                'popularity': movie.get('popularity', 0),
                'genre_ids': movie.get('genre_ids', [])
            })

        return {"movies": movies, "genre": genre, "count": len(movies)}
    except Exception as e:
        return {"error": f"Unexpected error in movie recommendations: {str(e)}"}


@tool
def get_song_recommendations(genre: str, max_results: int = 5) -> Dict[str, Any]:
    """Get song recommendations by genre from Spotify API."""
    try:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            return {"error": "Spotify API credentials not configured"}

        # Get access token
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }, timeout=10)

        if auth_response.status_code != 200:
            return {"error": f"Spotify authentication failed: {auth_response.status_code}"}

        auth_data = auth_response.json()
        access_token = auth_data.get('access_token')

        if not access_token:
            return {"error": "Failed to get Spotify access token"}

        # Get available genres
        headers = {'Authorization': f'Bearer {access_token}'}
        genres_url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
        genres_data = safe_api_request(genres_url, headers=headers)

        if "error" in genres_data:
            return genres_data

        available_genres = genres_data.get('genres', [])

        # Find matching genre
        genre_lower = genre.lower()
        matching_genre = None
        for g in available_genres:
            if genre_lower in g or g in genre_lower:
                matching_genre = g
                break

        if not matching_genre:
            matching_genre = available_genres[0] if available_genres else 'pop'

        # Get recommendations
        rec_url = 'https://api.spotify.com/v1/recommendations'
        rec_params = {
            'limit': min(max_results, 20),
            'seed_genres': matching_genre
        }
        rec_data = safe_api_request(rec_url, headers=headers, params=rec_params)

        if "error" in rec_data:
            return rec_data

        songs = []
        for track in rec_data.get('tracks', [])[:max_results]:
            artists = [artist['name'] for artist in track.get('artists', [])]
            album_images = track.get('album', {}).get('images', [])
            image_url = album_images[0]['url'] if album_images else ''

            songs.append({
                'name': track.get('name', 'Unknown'),
                'artists': artists,
                'album': track.get('album', {}).get('name', 'Unknown'),
                'preview_url': track.get('preview_url', ''),
                'image_url': image_url,
                'external_url': track.get('external_urls', {}).get('spotify', ''),
                'duration_ms': track.get('duration_ms', 0),
                'popularity': track.get('popularity', 0),
                'explicit': track.get('explicit', False)
            })

        return {"songs": songs, "genre": matching_genre, "count": len(songs)}
    except Exception as e:
        return {"error": f"Unexpected error in song recommendations: {str(e)}"}


@tool
def get_blog_recommendations(topic: str, max_results: int = 5) -> Dict[str, Any]:
    """Get blog recommendations by topic using web search."""
    try:
        # Use DuckDuckGo search to find blog posts
        search_query = f"{topic} blog posts articles"
        search_results = search_tool.run(search_query)

        # Parse search results (this is a simplified approach)
        blogs = []

        # Since we can't easily parse DuckDuckGo results, we'll provide a structured response
        # with generic blog recommendations
        blog_suggestions = [
            {
                'title': f"Top {topic} Insights and Trends",
                'url': f"https://medium.com/search?q={topic.replace(' ', '%20')}",
                'description': f"Discover the latest insights and trends about {topic} from industry experts and thought leaders.",
                'source': 'Medium',
                'image': 'https://miro.medium.com/max/1200/1*JLYg5F4J5LJpdlTgixgBiw.png'
            },
            {
                'title': f"Complete Guide to {topic}",
                'url': f"https://www.reddit.com/search/?q={topic.replace(' ', '%20')}",
                'description': f"Community discussions and expert advice about {topic} from Reddit.",
                'source': 'Reddit',
                'image': 'https://www.redditinc.com/assets/images/site/reddit-logo.png'
            },
            {
                'title': f"{topic} Resources and Tutorials",
                'url': f"https://dev.to/search?q={topic.replace(' ', '%20')}" if 'tech' in topic.lower() or 'programming' in topic.lower() else f"https://www.google.com/search?q={topic.replace(' ', '+')}+blog",
                'description': f"Comprehensive resources and tutorials about {topic}.",
                'source': 'Dev.to' if 'tech' in topic.lower() else 'Web Search',
                'image': 'https://res.cloudinary.com/practicaldev/image/fetch/s--0UiMFgbU--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_880/https://thepracticaldev.s3.amazonaws.com/i/6hqmcjaxbgbon8ydw93z.png'
            }
        ]

        blogs = blog_suggestions[:max_results]

        return {"blogs": blogs, "topic": topic, "count": len(blogs), "search_results": search_results[:200]}
    except Exception as e:
        return {"error": f"Unexpected error in blog recommendations: {str(e)}"}


@tool
def get_youtube_videos(topic: str, max_results: int = 5) -> Dict[str, Any]:
    """Search for YouTube videos on a specific topic."""
    try:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return {"error": "YouTube API key not configured"}

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": topic,
            "maxResults": min(max_results, 25),
            "type": "video",
            "key": api_key,
            "order": "relevance",
            "safeSearch": "moderate"
        }

        data = safe_api_request(url, params=params)
        if "error" in data:
            return data

        videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId', '')

            videos.append({
                'title': snippet.get('title', 'Unknown'),
                'channel': snippet.get('channelTitle', 'Unknown'),
                'description': snippet.get('description', 'No description available')[:200] + "..." if snippet.get(
                    'description', '') else 'No description available',
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'publishedAt': snippet.get('publishedAt', 'Unknown'),
                'videoId': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'channelId': snippet.get('channelId', ''),
                'embed_url': f"https://www.youtube.com/embed/{video_id}"
            })

        return {"videos": videos, "topic": topic, "count": len(videos)}
    except Exception as e:
        return {"error": f"Unexpected error in YouTube recommendations: {str(e)}"}


@tool
def search_general_content(query: str) -> Dict[str, Any]:
    """Search for general content using DuckDuckGo."""
    try:
        results = search_tool.run(query)
        return {
            "query": query,
            "results": results,
            "source": "DuckDuckGo"
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


# Combine all tools
def get_all_tools():
    """Return all available tools for the content recommendation system."""
    return [
        search_general_content,
        get_book_recommendations,
        get_movie_recommendations,
        get_song_recommendations,
        get_blog_recommendations,
        get_youtube_videos
    ]


# Tool validation function
def validate_tool_configuration():
    """Validate that all required API keys are configured."""
    required_keys = {
        "GOOGLE_BOOKS_API_KEY": "Google Books API",
        "TMDB_API_KEY": "The Movie Database API",
        "SPOTIFY_CLIENT_ID": "Spotify Client ID",
        "SPOTIFY_CLIENT_SECRET": "Spotify Client Secret",
        "YOUTUBE_API_KEY": "YouTube Data API"
    }

    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"{key} ({description})")

    if missing_keys:
        print("Warning: The following API keys are not configured:")
        for key in missing_keys:
            print(f"  - {key}")
        print("Some recommendation features may not work properly.")
        return False
    else:
        print("All API keys are configured.")
        return True


if __name__ == "__main__":
    # Test tool configuration
    validate_tool_configuration()