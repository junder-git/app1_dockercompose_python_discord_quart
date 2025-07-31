import aiohttp

async def get_playlist_videos(api_key, playlist_id, page_token=None, max_results=25, cache_manager=None):
    """
    Get videos from a YouTube playlist with pagination support
    
    Args:
        api_key (str): YouTube API key
        playlist_id (str): YouTube playlist ID
        page_token (str, optional): Token for pagination
        max_results (int): Maximum results per page
        cache_manager (CacheManager, optional): Cache manager instance
        
    Returns:
        tuple: (videos, next_page_token, total_results)
    """
    # If no API key, return empty results
    if not api_key:
        return [], None, 0
        
    # For playlists, we don't cache results with page tokens to avoid complexity
    cache_key = f"playlist_videos_{playlist_id}"
    
    # Try to get from cache if cache manager provided and no page token
    if cache_manager and page_token is None:
        cached_result = cache_manager.get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
    
    videos = []
    next_page_token = None
    total_results = 0
    
    async with aiohttp.ClientSession() as session:
        url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': playlist_id,
            'key': api_key,
            'maxResults': max_results
        }
        
        # Add page token if provided
        if page_token:
            params['pageToken'] = page_token
            
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    
                    # Get total results and next page token
                    if 'pageInfo' in results and 'totalResults' in results['pageInfo']:
                        total_results = results['pageInfo']['totalResults']
                    
                    if 'nextPageToken' in results:
                        next_page_token = results['nextPageToken']
                    
                    if 'items' in results:
                        for item in results['items']:
                            # Get video details - sometimes videoId is in different locations
                            video_id = None
                            if 'contentDetails' in item and 'videoId' in item['contentDetails']:
                                video_id = item['contentDetails']['videoId']
                            elif 'snippet' in item and 'resourceId' in item['snippet'] and 'videoId' in item['snippet']['resourceId']:
                                video_id = item['snippet']['resourceId']['videoId']
                            
                            if video_id:
                                video = {
                                    'id': video_id,
                                    'title': item['snippet']['title'],
                                    'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                    'channel': item['snippet']['channelTitle'] if 'channelTitle' in item['snippet'] else 'Unknown'
                                }
                                videos.append(video)
        except Exception as e:
            print(f"Error getting playlist videos: {e}")
    
    # Only cache first page results (without page token)
    result = (videos, next_page_token, total_results)
    if cache_manager and page_token is None:
        cache_manager.add_to_cache(cache_key, result)
    
    return result