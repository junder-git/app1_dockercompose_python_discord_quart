"""
YouTube API Blueprint for Quart
"""
from quart import Blueprint, request, current_app

# Create the blueprint
youtube_api_blueprint = Blueprint('youtube_api', __name__, url_prefix='/api/youtube')

@youtube_api_blueprint.route('/search')
async def search_route():
    """Search YouTube for videos, playlists, or both"""
    youtube_client = current_app.youtube_client
    
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'comprehensive')
    max_results = int(request.args.get('max_results', 10))
    
    # If no query, return empty results
    if not query:
        return {
            "videos": [],
            "playlists": []
        }
    
    # Search based on type
    videos = []
    playlists = []
    
    if search_type in ['video', 'comprehensive']:
        videos = await youtube_client.search_videos(query, max_results)
        
    if search_type in ['playlist', 'comprehensive']:
        playlists = await youtube_client.search_playlists(query, max_results)
    
    return {
        "query": query,
        "videos": videos,
        "playlists": playlists
    }

@youtube_api_blueprint.route('/video/<video_id>')
async def video_details_route(video_id):
    """Get details about a YouTube video"""
    youtube_client = current_app.youtube_client
    
    video_details = await youtube_client.get_video_details(video_id)
    return video_details

@youtube_api_blueprint.route('/playlist/<playlist_id>')
async def playlist_details_route(playlist_id):
    """Get details about a YouTube playlist"""
    youtube_client = current_app.youtube_client
    
    # Get page token for pagination
    page_token = request.args.get('page_token')
    max_results = int(request.args.get('max_results', 25))
    
    # Get playlist details
    playlist_details = await youtube_client.get_playlist_details(playlist_id)
    
    # Get playlist videos
    videos, next_page_token, total_results = await youtube_client.get_playlist_videos(
        playlist_id, page_token, max_results
    )
    
    return {
        "playlist_details": playlist_details,
        "items": videos,
        "next_page_token": next_page_token,
        "total_results": total_results
    }

@youtube_api_blueprint.route('/video-info')
async def video_url_info_route():
    """Extract information from a YouTube URL"""
    youtube_client = current_app.youtube_client
    
    url = request.args.get('url', '')
    if not url:
        return {"error": "No URL provided"}, 400
    
    # Check if it's a playlist URL
    playlist_id = youtube_client.extract_playlist_id(url)
    if playlist_id:
        playlist_details = await youtube_client.get_playlist_details(playlist_id)
        return {
            "type": "playlist",
            "playlist_id": playlist_id,
            "playlist_details": playlist_details
        }
    
    # Check if it's a video URL
    video_id = youtube_client.extract_video_id(url)
    if video_id:
        video_info = await youtube_client.get_video_details(video_id)
        return {
            "type": "video",
            "video_id": video_id,
            "video_info": video_info
        }
    
    # If neither, assume it's a search query
    videos = await youtube_client.search_videos(url, 1)
    if videos:
        video_info = await youtube_client.get_video_details(videos[0]['id'])
        return {
            "type": "search",
            "video_id": videos[0]['id'],
            "video_info": video_info
        }
    
    return {"error": "Could not parse URL or find results"}, 400

@youtube_api_blueprint.route('/extract-id', methods=['POST'])
async def extract_id_route():
    """Extract video or playlist ID from a URL"""
    youtube_client = current_app.youtube_client
    data = await request.get_json()
    
    url = data.get('url', '')
    if not url:
        return {"error": "No URL provided"}, 400
    
    # Try to extract playlist ID first
    playlist_id = youtube_client.extract_playlist_id(url)
    if playlist_id:
        return {
            "type": "playlist",
            "id": playlist_id,
            "url": youtube_client.normalize_playlist_url(url)
        }
    
    # Then try to extract video ID
    video_id = youtube_client.extract_video_id(url)
    if video_id:
        return {
            "type": "video",
            "id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }
    
    return {"error": "Could not extract ID from URL"}, 400