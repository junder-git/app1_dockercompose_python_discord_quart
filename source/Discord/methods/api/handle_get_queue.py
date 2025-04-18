"""
handle_get_queue method for Discord bot
Handles API requests to get queue information
"""
from aiohttp import web

async def handle_get_queue(self, request):
    """
    Return the current queue for a guild/channel
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with queue information
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        guild_id = request.query.get('guild_id')
        channel_id = request.query.get('channel_id')
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        queue_id = self.get_queue_id(guild_id, channel_id)
        current_track = self.currently_playing.get(queue_id)
        
        # Check if the bot is connected to this voice channel
        voice_client, _ = await self.get_voice_client(guild_id, channel_id)
        is_connected = voice_client is not None
        
        return web.json_response({
            "queue": self.music_queues[queue_id],
            "current_track": current_track,
            "is_connected": is_connected,
            "is_playing": is_connected and voice_client.is_playing(),
            "is_paused": is_connected and voice_client.is_paused()
        })
        
    except Exception as e:
        print(f"Error handling get_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)