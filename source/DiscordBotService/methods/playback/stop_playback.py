"""
stop_playback method for Discord bot
Stops playback and clears the queue
"""

async def stop_playback(self, guild_id, channel_id):
    """
    Stop playback and clear the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
    
    if not voice_client:
        return {"success": False, "message": "Not connected to a voice channel"}
    
    # Set flag to interrupt any ongoing playlist additions
    self.playlist_processing[queue_id] = True
    
    # Clear queue and stop playing
    self.music_queues[queue_id] = []
    self.currently_playing.pop(queue_id, None)
    
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
    
    return {"success": True, "message": "⏹️ Stopped playback and cleared queue"}