"""
Method to add multiple tracks to the queue
"""

async def add_multiple_to_queue(self, guild_id, channel_id, videos):
    """
    Add multiple tracks to the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        videos (list): List of video dictionaries with 'id' and 'title' keys
        
    Returns:
        dict: Summary of the operation
    """
    # Track overall success
    overall_success = True
    added_count = 0
    error_messages = []
    
    # Add each video individually since the bot API doesn't support batch adds yet
    for video in videos:
        video_id = video.get('id')
        video_title = video.get('title', 'Unknown Video')
        
        result = await self.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result.get('success'):
            added_count += 1
        else:
            overall_success = False
            error_messages.append(f"Error adding '{video_title}': {result.get('error')}")
    
    # Return a summary of the operation
    return {
        "success": overall_success or added_count > 0,  # Consider partial success as success
        "added_count": added_count,
        "total_count": len(videos),
        "message": f"Added {added_count} of {len(videos)} videos to queue",
        "errors": error_messages if error_messages else None
    }