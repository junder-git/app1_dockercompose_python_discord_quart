import aiohttp

async def search_videos(api_key, query, max_results=10, youtube_service=None):
    """
    Search YouTube for videos matching a query with additional details
    
    Args:
        api_key (str): YouTube API key
        query (str): Search query
        max_results (int): Maximum number of results to return
        youtube_service (YouTubeService, optional): YouTube service instance for duration parsing
            
    Returns:
        list: List of video objects with id, title, thumbnail, channel, duration
    """
    # If no API key, return empty results
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
            async with session.get(search_url, params=search_params) as search_response:
                if search_response.status == 200:
                    search_data = await search_response.json()
                    
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
                                        if youtube_service:
                                            duration = youtube_service.parse_duration(duration_str)
                                        else:
                                            # Fallback to a simple duration parser if no service provided
                                            from youtube_api_client.extractors.duration import parse_duration
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
            print(f"Error searching YouTube: {e}")
    
    return search_results