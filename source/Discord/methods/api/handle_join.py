"""
handle_join method for Discord bot
Handles API requests to join a voice channel
"""
import asyncio
from aiohttp import web

async def handle_join(self, request):
    """
    Handle join voice channel requests from the API
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with status and message
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        preserve_queue = data.get('preserve_queue', True)
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Get the guild
        guild = self.get_guild(int(guild_id))
        if not guild:
            return web.json_response({"error": "Guild not found"}, status=404)
        
        # Get the voice channel
        voice_channel = guild.get_channel(int(channel_id))
        if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
            return web.json_response({"error": "Voice channel not found"}, status=404)
        
        # Disconnect from any existing voice channel in this guild
        await self.disconnect_from_voice(guild_id, preserve_queue=preserve_queue)
        
        # Connect to the new voice channel
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
        
        if not voice_client:
            return web.json_response({"error": "Failed to connect to voice channel"}, status=500)
            
        # If there are songs in the queue and we're preserving the queue, start playback
        if preserve_queue and self.music_queues[queue_id] and queue_id not in self.currently_playing:
            asyncio.create_task(self.play_next(guild_id, channel_id))
        
        return web.json_response({
            "success": True, 
            "message": f"Joined {voice_channel.name}",
            "queue_id": queue_id
        })
        
    except Exception as e:
        print(f"Error handling join request: {e}")
        return web.json_response({"error": str(e)}, status=500)