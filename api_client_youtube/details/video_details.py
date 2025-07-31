import aiohttp
from api_client_youtube.extractors.duration import parse_duration

async def get_video_details(api_key, video_id, cache_manager=None):
    """
    Get details about a YouTube video
    
    Args:
        api_key (str): YouTube API key
        video_id (str): YouTube video ID
        cache_manager (CacheManager, optional): Cache manager instance
        
    Returns:
        dict: Video details including title, channel, thumbnail, duration
    """
    # If no API key, return basic info
    if not api_key:
        return {
            'id': video_id,
            'title': 'Unknown Video',
            'channel': 'Unknown Channel',
            'thumbnail': '',
            'duration': 0
        }
        
    cache_key = f"video_details_{video_id}"
    
    # Try to get from cache if cache manager provided
    if cache_manager:
        cached_result = cache_manager.get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
    async with aiohttp.ClientSession() as session:
        url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': api_key
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    if 'items' in results and len(results['items']) > 0:
                        item = results['items'][0]
                        
                        # Parse duration from ISO 8601 format
                        duration_str = item['contentDetails']['duration'] if 'contentDetails' in item and 'duration' in item['contentDetails'] else 'PT0S'
                        duration_seconds = parse_duration(duration_str)
                        
                        # Extract video details
                        details = {
                            'id': video_id,
                            'title': item['snippet']['title'],
                            'channel': item['snippet']['channelTitle'],
                            'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                            'duration': duration_seconds
                        }
                        
                        # Cache the result if cache manager provided
                        if cache_manager:
                            cache_manager.add_to_cache(cache_key, details)
                        return details
        except Exception as e:
            print(f"Error getting video details: {e}")
    
    # Return default values if something went wrong
    default_details = {
        'id': video_id,
        'title': 'Unknown Video',
        'channel': 'Unknown Channel',
        'thumbnail': '',
        'duration': 0
    }
    
    # Still cache the default to prevent repeated API failures
    if cache_manager:
        cache_manager.add_to_cache(cache_key, default_details)
    return default_details