"""
skip_track method for Discord bot
Skips the currently playing track in the queue
"""

async def skip_track(self, guild_id, channel_id):
    """
    Skip the current track
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
    
    if not voice_client:
        return {"success": False, "message": "Not connected to a voice channel"}
    
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        return {"success": True, "message": "⏭️ Skipped to next track"}
    else:
        return {"success": False, "message": "Nothing is playing to skip"}