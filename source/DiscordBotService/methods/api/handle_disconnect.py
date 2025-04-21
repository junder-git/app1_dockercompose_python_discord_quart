"""
handle_disconnect method for Discord bot
Handles API requests to disconnect from voice channels
"""
from aiohttp import web

async def handle_disconnect(self, request):
    """
    Handle disconnect from voice channel requests
    
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
        preserve_queue = data.get('preserve_queue', True)
        
        if not guild_id:
            return web.json_response({"error": "Missing guild_id parameter"}, status=400)
        
        # Use the shared disconnect method
        result = await self.disconnect_from_voice(guild_id, channel_id, preserve_queue)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=404)
            
    except Exception as e:
        print(f"Error handling disconnect request: {e}")
        return web.json_response({"error": str(e)}, status=500)