"""
API Blueprint for Discord Bot
Handles API server setup and API endpoints
"""
from aiohttp import web
import asyncio
import types
import json

def apply(bot):
    """
    Apply API blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    bot.start_api_server = types.MethodType(start_api_server, bot)
    bot.setup_hook = types.MethodType(setup_hook, bot)
    
    # Register all API handler methods
    for handler_name, handler_func in get_api_handlers().items():
        setattr(bot, handler_name, types.MethodType(handler_func, bot))

async def setup_hook(self):
    """Called when the bot starts up"""
    # Start the API server
    await self.start_api_server()
    print("API server started")

async def start_api_server(self):
    """
    Start a web server to handle API requests from the Quart app
    """
    app = web.Application()
    app.add_routes([
        # Guild information
        web.get('/api/guild_count', self.handle_guild_count),
        web.get('/api/guild_ids', self.handle_guild_ids),
        
        # Queue management
        web.post('/api/add_to_queue', self.handle_add_to_queue),
        web.get('/api/get_queue', self.handle_get_queue),
        web.post('/api/clear_queue', self.handle_clear_queue),
        web.post('/api/shuffle_queue', self.handle_shuffle_queue),
        web.post('/api/reorder_queue', self.handle_reorder_queue),
        
        # Playback control
        web.post('/api/skip', self.handle_skip),
        web.post('/api/pause', self.handle_pause),
        web.post('/api/resume', self.handle_resume),
        
        # Voice connection
        web.post('/api/join', self.handle_join),
        web.post('/api/disconnect', self.handle_disconnect),
        
        # User information
        web.get('/api/get_user_voice_state', self.handle_get_user_voice_state),
    ])
    
    # Get API port from environment or use default
    api_port = 5001
    
    runner = web.AppRunner(app)
    await runner.setup()
    self.api_server = web.TCPSite(runner, '0.0.0.0', api_port)
    await self.api_server.start()
    print(f"API server started at http://0.0.0.0:{api_port}")

def get_api_handlers():
    """
    Get all API handler methods
    
    Returns:
        dict: Dictionary of handler names to handler functions
    """
    return {
        'handle_guild_count': handle_guild_count,
        'handle_guild_ids': handle_guild_ids,
        'handle_add_to_queue': handle_add_to_queue,
        'handle_get_queue': handle_get_queue,
        'handle_clear_queue': handle_clear_queue,
        'handle_shuffle_queue': handle_shuffle_queue,
        'handle_reorder_queue': handle_reorder_queue,
        'handle_skip': handle_skip,
        'handle_pause': handle_pause,
        'handle_resume': handle_resume,
        'handle_join': handle_join,
        'handle_disconnect': handle_disconnect,
        'handle_get_user_voice_state': handle_get_user_voice_state,
    }

# API Handler Methods

async def handle_guild_count(self, request):
    """Handle guild count requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    return web.json_response({"count": len(self.guilds)})

async def handle_guild_ids(self, request):
    """Handle guild IDs requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    guild_ids = [str(guild.id) for guild in self.guilds]
    return web.json_response({"guild_ids": guild_ids})

async def handle_add_to_queue(self, request):
    """Handle adding a track to the queue"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        video_id = data.get('video_id')
        video_title = data.get('video_title', 'Unknown title')
        
        if not all([guild_id, channel_id, video_id]):
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # First, ensure we're connected to the voice channel
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
        
        if not voice_client:
            return web.json_response({"error": "Failed to connect to voice channel"}, status=500)
        
        # Then add the track to the queue
        result = await self.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=500)
            
    except Exception as e:
        print(f"Error handling add_to_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_get_queue(self, request):
    """Return the current queue for a guild/channel"""
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

async def handle_clear_queue(self, request):
    """Handle requests to clear a queue"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')  # Optional
        
        if not guild_id:
            return web.json_response({"error": "Missing guild_id parameter"}, status=400)
        
        # Use the shared clear_queue method
        result = await self.clear_queue(guild_id, channel_id)
        
        return web.json_response(result)
        
    except Exception as e:
        print(f"Error handling clear_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_shuffle_queue(self, request):
    """Handle requests to shuffle the queue"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Use the shared shuffle method
        result = await self.shuffle_queue(guild_id, channel_id)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling shuffle_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_reorder_queue(self, request):
    """Handle requests to reorder tracks in the queue"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        old_index = data.get('old_index')
        new_index = data.get('new_index')
        
        if not all([guild_id, channel_id, old_index is not None, new_index is not None]):
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Use the shared reorder method
        result = await self.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling reorder_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_skip(self, request):
    """Handle skip track requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Use the shared skip method
        result = await self.skip_track(guild_id, channel_id)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling skip request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_pause(self, request):
    """Handle pause playback requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        voice_client, _ = await self.get_voice_client(guild_id, channel_id)
        
        if not voice_client:
            return web.json_response({"error": "Not connected to a voice channel"}, status=400)
        
        if voice_client.is_playing():
            voice_client.pause()
            
            # Update control panels
            await self.update_control_panel(guild_id, channel_id)
            
            return web.json_response({"success": True, "message": "Paused playback"})
        else:
            return web.json_response({"error": "Not playing"}, status=400)
            
    except Exception as e:
        print(f"Error handling pause request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_resume(self, request):
    """Handle resume playback requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id')
        
        if not guild_id or not channel_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        voice_client, _ = await self.get_voice_client(guild_id, channel_id)
        
        if not voice_client:
            return web.json_response({"error": "Not connected to a voice channel"}, status=400)
        
        if voice_client.is_paused():
            voice_client.resume()
            
            # Update control panels
            await self.update_control_panel(guild_id, channel_id)
            
            return web.json_response({"success": True, "message": "Resumed playback"})
        else:
            return web.json_response({"error": "Not paused"}, status=400)
            
    except Exception as e:
        print(f"Error handling resume request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_join(self, request):
    """Handle join voice channel requests"""
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

async def handle_disconnect(self, request):
    """Handle disconnect from voice channel requests"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        guild_id = data.get('guild_id')
        user_id = data.get('user_id')
        preserve_queue = data.get('preserve_queue', False)
        
        if not guild_id:
            return web.json_response({"error": "Missing guild_id parameter"}, status=400)
        
        # Use the shared disconnect method
        result = await self.disconnect_from_voice(guild_id, preserve_queue=preserve_queue)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=404)
            
    except Exception as e:
        print(f"Error handling disconnect request: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_get_user_voice_state(self, request):
    """Handle requests to get a user's voice state"""
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        # Get parameters
        guild_id = request.query.get('guild_id')
        user_id = request.query.get('user_id')
        
        if not guild_id or not user_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Get the guild
        guild = self.get_guild(int(guild_id))
        if not guild:
            return web.json_response({"error": "Guild not found"}, status=404)
        
        # Get the member
        try:
            member = await guild.fetch_member(int(user_id))
        except Exception:
            return web.json_response({"error": "Member not found"}, status=404)
        
        # Check if user is in a voice channel
        if not member.voice:
            return web.json_response({"voice_state": None})
        
        # Return voice state information
        voice_state = {
            "channel_id": str(member.voice.channel.id),
            "channel_name": member.voice.channel.name,
            "mute": member.voice.mute,
            "deaf": member.voice.deaf,
            "self_mute": member.voice.self_mute,
            "self_deaf": member.voice.self_deaf
        }
        
        return web.json_response({"voice_state": voice_state})
        
    except Exception as e:
        print(f"Error handling get_user_voice_state request: {e}")
        return web.json_response({"error": str(e)}, status=500)