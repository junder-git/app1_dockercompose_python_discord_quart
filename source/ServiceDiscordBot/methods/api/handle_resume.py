"""
handle_resume method for Discord bot
Handles API requests to resume playback
"""
from aiohttp import web

async def handle_resume(self, request):
    """
    Handle resume playback requests
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with result
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
            voice_client.resume()
            
            # Update control panels
            await self.update_control_panel(guild_id, channel_id)
            
            return web.json_response({"success": True, "message": "Resumed playback"})
        else:
            return web.json_response({"error": "Not paused"}, status=400)
            
    except Exception as e:
        print(f"Error handling resume request: {e}")
        return web.json_response({"error": str(e)}, status=500)