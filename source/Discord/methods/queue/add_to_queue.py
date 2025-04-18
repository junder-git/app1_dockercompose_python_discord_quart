"""
add_to_queue method for Discord bot
Adds a track to the queue and starts playing if needed
"""
import asyncio

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