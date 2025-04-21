"""
shuffle_queue method for Discord bot
Randomly shuffles the music queue
"""
import random

async def shuffle_queue(self, guild_id, channel_id):
    """
    Shuffle the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    queue_id = self.get_queue_id(guild_id, channel_id)
    
    if not self.music_queues[queue_id]:
        return {"success": False, "message": "Queue is empty, nothing to shuffle"}
    
    random.shuffle(self.music_queues[queue_id])
    return {"success": True, "message": "🔀 Queue shuffled"}