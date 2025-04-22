"""
Search Blueprint for Music Central Service
Handles YouTube search functionality
"""
from quart import Blueprint, request, current_app
import yt_dlp
import aiohttp
import re

# Create blueprint
search_blueprint = Blueprint('search', __name__, url_prefix='/api')

@search_blueprint.route('/search', methods=['GET'])
async def search_route():
    """Search YouTube for videos matching a query"""
    query = request.args.get('q')
    max_results = int(request.args.get('max_results', 10))
    
    if not query:
        return {"error": "Missing query parameter"}, 400
    
    # Try to use the YouTube API first (more reliable)
    youtube_client = current_app.youtube_client
    results = await search_videos_with_api(query, max_results, youtube_client.api_key)
    
    # Fall back to yt-dlp if API fails
    if not results:
        results = await search_videos_with_ytdlp(query, max_results)
    
    return {"results": results}

async def search_videos_with_api(query, max_results, api_key):
    """
    Search YouTube for videos using the API
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        api_key (str): YouTube API key
        
    Returns:
        list: List of video objects with id, title, thumbnail, channel, duration
    """
    if not api_key:
        return []
    
    search_results = []
    async with aiohttp.ClientSession() as session:
        # First, perform the search to get video IDs
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        search_params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'maxResults': max_results,
            'type': 'video'
        }
        
        try:
            async with session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    
                    if 'items' in search_data:
                        # Extract video IDs
                        video_ids = [item['id']['videoId'] for item in search_data['items']]
                        
                        # Get details for these videos in a single API call
                        details_url = 'https://www.googleapis.com/youtube/v3/videos'
                        details_params = {
                            'part': 'snippet,contentDetails',
                            'id': ','.join(video_ids),
                            'key': api_key
                        }
                        
                        async with session.get(details_url, params=details_params) as details_response:
                            if details_response.status == 200:
                                details_data = await details_response.json()
                                
                                # Create a mapping of video ID to details
                                video_details = {}
                                for item in details_data.get('items', []):
                                    if 'contentDetails' in item:
                                        duration_str = item['contentDetails'].get('duration', 'PT0S')
                                        duration = parse_duration(duration_str)
                                        
                                        video_details[item['id']] = {
                                            'duration': duration
                                        }
                                
                                # Combine search results with details
                                for item in search_data['items']:
                                    video_id = item['id']['videoId']
                                    video = {
                                        'id': video_id,
                                        'title': item['snippet']['title'],
                                        'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                            if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                            else '',
                                        'channel': item['snippet']['channelTitle'],
                                        'duration': video_details.get(video_id, {}).get('duration', 0)
                                    }
                                    search_results.append(video)
        except Exception as e:
            print(f"Error searching YouTube with API: {e}")
    
    return search_results

async def search_videos_with_ytdlp(query, max_results):
    """
    Search YouTube for videos using yt-dlp (fallback method)
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of video objects with id, title, thumbnail, channel, duration
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'no_color': True,
        'default_search': 'ytsearch',
        'max_downloads': max_results
    }
    
    search_query = f"ytsearch{max_results}:{query}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info:
                results = []
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', 'Unknown Title'),
                            'thumbnail': entry.get('thumbnail', ''),
                            'channel': entry.get('uploader', 'Unknown Channel'),
                            'duration': entry.get('duration', 0)
                        })
                return results
    except Exception as e:
        print(f"Error searching with yt-dlp: {e}")
    
    return []

def parse_duration(duration_str):
    """
    Parse ISO 8601 duration to seconds
    e.g. PT1H30M15S -> 5415 seconds
    
    Args:
        duration_str (str): ISO 8601 duration string
        
    Returns:
        int: Duration in seconds
    """
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    hour_match = re.search(r'(\d+)H', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
    
    # Extract minutes
    minute_match = re.search(r'(\d+)M', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))
    
    # Extract seconds
    second_match = re.search(r'(\d+)S', duration_str)
    if second_match:
        seconds = int(second_match.group(1))
    
    return hours * 3600 + minutes * 60 + seconds