"""
Method to skip the current track in the queue
"""

async def skip_track(self, guild_id, channel_id):
    """
    Skip the current track in the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result of the operation
    """
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id
    }
    return await self._post_request("skip", data)