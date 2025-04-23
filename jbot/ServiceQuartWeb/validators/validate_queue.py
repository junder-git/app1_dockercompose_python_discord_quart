"""
Queue validation functions
"""

async def validate_add_to_queue(form_data):
    """
    Validate parameters for adding a track to the queue
    
    Args:
        form_data: Form data from request
        
    Returns:
        tuple: (is_valid, errors) - Boolean indicating if valid and list of error messages
    """
    errors = []
    
    # Required fields
    channel_id = form_data.get('channel_id')
    video_id = form_data.get('video_id')
    
    if not channel_id:
        errors.append("Missing channel ID")
    
    if not video_id:
        errors.append("Missing video ID")
    
    return len(errors) == 0, errors

async def validate_add_multiple(form_data):
    """
    Validate parameters for adding multiple tracks to the queue
    
    Args:
        form_data: Form data from request
        
    Returns:
        tuple: (is_valid, errors, videos) - Boolean indicating if valid, error messages, 
               and processed video data
    """
    errors = []
    videos = []
    
    # Required fields
    channel_id = form_data.get('channel_id')
    
    if not channel_id:
        errors.append("Missing channel ID")
    
    # Extract video IDs and titles
    video_ids = []
    video_titles = []
    
    for key, value in form_data.items():
        if key.startswith('video_ids-'):
            video_ids.append(value)
        elif key.startswith('video_titles-'):
            video_titles.append(value)
    
    if not video_ids:
        errors.append("No videos selected")
    
    # Create videos list
    for i, video_id in enumerate(video_ids):
        title = "Unknown Video"
        if i < len(video_titles):
            title = video_titles[i]
        
        videos.append({
            'id': video_id,
            'title': title
        })
    
    return len(errors) == 0, errors, videos

async def validate_add_playlist(form_data):
    """
    Validate parameters for adding an entire playlist to the queue
    
    Args:
        form_data: Form data from request
        
    Returns:
        tuple: (is_valid, errors) - Boolean indicating if valid and list of error messages
    """
    errors = []
    
    # Required fields
    playlist_id = form_data.get('playlist_id')
    channel_id = form_data.get('channel_id')
    
    if not playlist_id:
        errors.append("Missing playlist ID")
    
    if not channel_id:
        errors.append("Missing channel ID")
    
    return len(errors) == 0, errors