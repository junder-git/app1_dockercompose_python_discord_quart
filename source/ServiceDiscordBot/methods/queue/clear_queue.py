"""
clear_queue method for Discord bot
Clears queue(s) for a guild, optionally for a specific channel
"""

async def clear_queue(self, guild_id, channel_id=None):
    """
    Clear queue(s) for a guild, optionally for a specific channel
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str, optional): Discord channel ID. If not provided, all queues for the guild are cleared.
        
    Returns:
        dict: Result containing success status and message
    """
    queues_cleared = 0
    channel_ids = []
    
    if channel_id:
        # Clear a specific queue
        queue_id = self.get_queue_id(guild_id, channel_id)
        self.music_queues[queue_id] = []
        self.currently_playing.pop(queue_id, None)
        channel_ids.append(channel_id)
        queues_cleared = 1
    else:
        # Clear all queues for this guild
        for queue_id in list(self.music_queues.keys()):
            if queue_id.startswith(f"{guild_id}_"):
                self.music_queues[queue_id] = []
                self.currently_playing.pop(queue_id, None)
                this_channel_id = queue_id.split('_')[1]
                channel_ids.append(this_channel_id)
                queues_cleared += 1
    
    # Update control panels
    for ch_id in channel_ids:
        await self.update_control_panel(guild_id, ch_id)
    
    return {
        "success": True,
        "message": f"Cleared {queues_cleared} queue(s) for guild {guild_id}"
    }