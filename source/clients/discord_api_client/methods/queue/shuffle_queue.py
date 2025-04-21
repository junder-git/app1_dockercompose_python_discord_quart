"""
Method to shuffle the queue for a guild
"""

async def shuffle_queue(self, guild_id, channel_id):
    """
    Shuffle the queue for a guild
    
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
    return await self._post_request("shuffle_queue", data)