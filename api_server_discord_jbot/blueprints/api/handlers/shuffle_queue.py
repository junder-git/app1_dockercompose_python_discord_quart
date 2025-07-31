"""
Handler for shuffle queue API requests - calls the core shuffle_queue functionality
"""
from aiohttp import web
from ...commands.queue import shuffle_queue

async def handle_shuffle_queue(self, request):
    """
    Handle requests to shuffle the queue
    
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
        
        # Call the core shuffle_queue function
        result = await shuffle_queue(self, guild_id, channel_id)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling shuffle_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)