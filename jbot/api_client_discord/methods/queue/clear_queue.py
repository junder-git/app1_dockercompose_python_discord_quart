"""
Method to clear the queue for a guild
"""

async def clear_queue(self, guild_id):
    """
    Clear the queue for a guild
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        dict: Result of the operation
    """
    data = {
        "guild_id": guild_id
    }
    return await self._post_request("clear_queue", data)