import aiohttp

async def search_artists(api_key, query, max_results=10):
    """
    Search for YouTube channels (artists) based on a query
    
    Args:
        api_key (str): YouTube API key
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of channel objects with id, title, description, thumbnail
    """
    # If no API key, return empty results
    if not api_key:
        return []
        
    search_results = []
    async with aiohttp.ClientSession() as session:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'maxResults': max_results,
            'type': 'channel'  # Explicitly search for channels
        }
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    if 'items' in results:
                        for item in results['items']:
                            channel = {
                                'id': item['id']['channelId'],
                                'title': item['snippet']['title'],
                                'description': item['snippet'].get('description', ''),
                                'thumbnail': (
                                    item['snippet']['thumbnails']['medium']['url'] 
                                    if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                    else ''
                                )
                            }
                            search_results.append(channel)
        except Exception as e:
            print(f"Error searching YouTube channels: {e}")
    
    return search_results