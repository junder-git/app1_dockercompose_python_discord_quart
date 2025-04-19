"""
Method to reorder an item in the queue
"""

async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
    """
    Reorder an item in the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        old_index (int): Current position in the queue
        new_index (int): New position in the queue
        
    Returns:
        dict: Result of the operation
    """
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "old_index": old_index,
        "new_index": new_index
    }
    return await self._post_request("reorder_queue", data)