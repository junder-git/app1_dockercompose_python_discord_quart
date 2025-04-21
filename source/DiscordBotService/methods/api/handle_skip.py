"""
handle_skip method for Discord bot
Handles API requests to skip the current track
"""
from aiohttp import web

async def handle_skip(self, request):
    """
    Handle skip track requests
    
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
        
        # Use the shared skip method
        result = await self.skip_track(guild_id, channel_id)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling skip request: {e}")
        return web.json_response({"error": str(e)}, status=500)