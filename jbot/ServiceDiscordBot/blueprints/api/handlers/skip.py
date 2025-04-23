"""
Handler for skip track API requests - calls the core skip functionality
"""
from aiohttp import web
from ...commands.skip import skip_track

async def handle_skip(self, request):
    """
    Handle skip track requests
    
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
        
        # Call the core skip functionality from the commands module
        result = await skip_track(self, guild_id, channel_id)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling skip request: {e}")
        return web.json_response({"error": str(e)}, status=500)