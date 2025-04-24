"""
Method to join a voice channel in a guild
"""

async def join_voice_channel(self, guild_id, channel_id):
    """
    Join a voice channel in a guild
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord voice channel ID
        
    Returns:
        dict: Result of the join operation
    """
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "preserve_queue": True
    }
    return await self._post_request("join", data)