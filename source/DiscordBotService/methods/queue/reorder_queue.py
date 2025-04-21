"""
reorder_queue method for Discord bot
Moves a track in the queue from one position to another
"""

async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
    """
    Move a track in the queue from old_index to new_index
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        old_index (int): Current position of the track
        new_index (int): New position for the track
        
    Returns:
        dict: Result containing success status and message
    """
    queue_id = self.get_queue_id(guild_id, channel_id)
    
    # Make sure indices are valid
    if not self.music_queues[queue_id] or old_index < 0 or old_index >= len(self.music_queues[queue_id]) or \
    new_index < 0 or new_index >= len(self.music_queues[queue_id]):
        return {"success": False, "message": "Invalid index"}
    
    # Move the track from old_index to new_index
    track = self.music_queues[queue_id].pop(old_index)
    self.music_queues[queue_id].insert(new_index, track)
    
    # Update control panels
    await self.update_control_panel(guild_id, channel_id)
    
    return {
        "success": True,
        "message": f"Track moved from position {old_index} to {new_index}"
    }