"""
Method to disconnect from a voice channel in a guild
"""

async def disconnect_voice_channel(self, guild_id, user_id, preserve_queue=False):
    """
    Disconnect from a voice channel in a guild
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID requesting disconnect
        preserve_queue (bool): Whether to preserve the music queue
        
    Returns:
        dict: Result of the disconnect operation
    """
    data = {
        "guild_id": guild_id,
        "user_id": user_id,
        "preserve_queue": preserve_queue
    }
    return await self._post_request("disconnect", data)