"""
Queue Blueprint for Discord Bot
Handles music queue management
"""
import types
import asyncio
import random

def apply(bot):
    """
    Apply queue blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind queue methods to the bot
    bot.add_to_queue = types.MethodType(add_to_queue, bot)
    bot.clear_queue = types.MethodType(clear_queue, bot)
    bot.shuffle_queue = types.MethodType(shuffle_queue, bot)
    bot.reorder_queue = types.MethodType(reorder_queue, bot)

async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
    """
    Add a track to the queue and start playing if needed
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        video_id (str): YouTube video ID
        video_title (str): YouTube video title
        
    Returns:
        dict: Result containing success status, message, and queue length
    """
    voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
    
    if not voice_client:
        return {"success": False, "message": "Could not connect to voice channel"}
    
    # Add to queue
    self.music_queues[queue_id].append({
        "id": video_id,
        "title": video_title,
        "url": f"https://www.youtube.com/watch?v={video_id}"
    })
    
    # If we're not playing anything in this queue, start playing
    if queue_id not in self.currently_playing:
        asyncio.create_task(self.play_next(guild_id, channel_id))
    
    # Update control panels
    await self.update_control_panel(guild_id, channel_id)
    
    return {
        "success": True, 
        "message": f"Added to queue: {video_title}",
        "queue_length": len(self.music_queues[queue_id])
    }

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
    
    # Update control panels
    await self.update_control_panel(guild_id, channel_id)
    
    return {"success": True, "message": "🔀 Queue shuffled"}

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

