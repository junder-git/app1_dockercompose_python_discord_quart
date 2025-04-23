"""
Method to add a track to the queue
"""

async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
    """
    Add a track to the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        video_id (str): YouTube video ID
        video_title (str): YouTube video title
        
    Returns:
        dict: Result of the operation
    """
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "video_id": video_id,
        "video_title": video_title
    }
    return await self._post_request("add_to_queue", data)