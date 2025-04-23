"""
Handler for disconnect from voice channel API requests - calls the core disconnect functionality
"""
from aiohttp import web
from ...commands.leave import disconnect_from_voice

async def handle_disconnect(self, request):
    """
    Handle disconnect from voice channel requests
    
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
        user_id = data.get('user_id')
        preserve_queue = data.get('preserve_queue', False)
        
        if not guild_id:
            return web.json_response({"error": "Missing guild_id parameter"}, status=400)
        
        # Call the core disconnect_from_voice function
        result = await disconnect_from_voice(self, guild_id, preserve_queue=preserve_queue)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=404)
            
    except Exception as e:
        print(f"Error handling disconnect request: {e}")
        return web.json_response({"error": str(e)}, status=500)