import aiohttp

async def get_playlist_details(api_key, playlist_id, cache_manager=None):
    """
    Get details about a YouTube playlist
    
    Args:
        api_key (str): YouTube API key
        playlist_id (str): YouTube playlist ID
        cache_manager (CacheManager, optional): Cache manager instance
        
    Returns:
        dict: Playlist details including title, channel, thumbnail, video count
    """
    # If no API key, return basic info
    if not api_key:
        return {
            'id': playlist_id,
            'title': 'Unknown Playlist',
            'channel': 'Unknown Channel',
            'thumbnail': '',
            'video_count': 0
        }
        
    cache_key = f"playlist_details_{playlist_id}"
    
    # Try to get from cache if cache manager provided
    if cache_manager:
        cached_result = cache_manager.get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
    async with aiohttp.ClientSession() as session:
        url = 'https://www.googleapis.com/youtube/v3/playlists'
        params = {
            'part': 'snippet,contentDetails',
            'id': playlist_id,
            'key': api_key
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    if 'items' in results and len(results['items']) > 0:
                        item = results['items'][0]
                        
                        # Extract playlist details
                        details = {
                            'id': playlist_id,
                            'title': item['snippet']['title'],
                            'channel': item['snippet']['channelTitle'],
                            'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                            'video_count': item['contentDetails']['itemCount'] if 'contentDetails' in item and 'itemCount' in item['contentDetails'] else 0
                        }
                        
                        # Cache the result if cache manager provided
                        if cache_manager:
                            cache_manager.add_to_cache(cache_key, details)
                        return details
        except Exception as e:
            print(f"Error getting playlist details: {e}")
    
    # Return default values if something went wrong
    default_details = {
        'id': playlist_id,
        'title': 'Unknown Playlist',
        'channel': 'Unknown Channel',
        'thumbnail': '',
        'video_count': 0
    }
    
    # Still cache the default to prevent repeated API failures
    if cache_manager:
        cache_manager.add_to_cache(cache_key, default_details)
    return default_details