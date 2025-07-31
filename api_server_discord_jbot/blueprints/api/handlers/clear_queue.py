"""
Handler for clear queue API requests - calls the core clear_queue functionality
"""
from aiohttp import web
from ...commands.queue import clear_queue

async def handle_clear_queue(self, request):
    """
    Handle requests to clear a queue
    
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
        channel_id = data.get('channel_id')  # Optional
        
        if not guild_id:
            return web.json_response({"error": "Missing guild_id parameter"}, status=400)
        
        # Call the core clear_queue function
        result = await clear_queue(self, guild_id, channel_id)
        
        return web.json_response(result)
        
    except Exception as e:
        print(f"Error handling clear_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)