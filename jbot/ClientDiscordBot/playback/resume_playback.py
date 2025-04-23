"""
Method to resume the current playback
"""

async def resume_playback(self, guild_id, channel_id):
    """
    Resume the current playback
    
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
    return await self._post_request("resume", data)