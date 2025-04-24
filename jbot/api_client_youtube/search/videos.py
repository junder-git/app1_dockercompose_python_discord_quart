import aiohttp

async def search_videos(api_key, query, max_results=10, cache_manager=None):
    """
    Search YouTube for videos matching a query
    
    Args:
        api_key (str): YouTube API key
        query (str): Search query
        max_results (int): Maximum number of results to return
        cache_manager (CacheManager, optional): Cache manager instance
        
    Returns:
        list: List of video objects with id, title, thumbnail, channel
    """
    # If no API key, return empty results
    if not api_key:
        return []
        
    cache_key = f"videos_{query}_{max_results}"
    
    # Try to get from cache if cache manager provided
    if cache_manager:
        cached_result = cache_manager.get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
    search_results = []
    async with aiohttp.ClientSession() as session:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'maxResults': max_results,
            'type': 'video'
        }
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    if 'items' in results:
                        for item in results['items']:
                            video = {
                                'id': item['id']['videoId'],
                                'title': item['snippet']['title'],
                                'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                'channel': item['snippet']['channelTitle']
                            }
                            search_results.append(video)
        except Exception as e:
            print(f"Error searching YouTube: {e}")
    
    # Cache results if cache manager provided
    if cache_manager:
        cache_manager.add_to_cache(cache_key, search_results)
    
    return search_results