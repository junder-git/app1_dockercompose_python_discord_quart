"""
Handler for resume playback API requests - calls toggle_playback functionality
"""
from aiohttp import web
from ...commands.pause import toggle_playback

async def handle_resume(self, request):
    """
    Handle resume playback requests
    
    Args:
        request: The aiohttp request object
        
    Returns:
        web.Response: JSON response with result or error
    """
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
            # Use the toggle_playback function which will resume the playback
            result = await toggle_playback(self, guild_id, channel_id)
            
            if result["success"]:
                return web.json_response({"success": True, "message": "Resumed playback"})
            else:
                return web.json_response({"error": result["message"]}, status=400)
        else:
            return web.json_response({"error": "Not paused"}, status=400)
            
    except Exception as e:
        print(f"Error handling resume request: {e}")
        return web.json_response({"error": str(e)}, status=500)