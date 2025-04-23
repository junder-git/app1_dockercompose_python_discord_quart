"""
Handler for reorder queue API requests - calls the core reorder_queue functionality
"""
from aiohttp import web
from ...commands.queue import reorder_queue

async def handle_reorder_queue(self, request):
    """
    Handle requests to reorder tracks in the queue
    
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
        old_index = data.get('old_index')
        new_index = data.get('new_index')
        
        if not all([guild_id, channel_id, old_index is not None, new_index is not None]):
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Call the core reorder_queue function
        result = await reorder_queue(self, guild_id, channel_id, old_index, new_index)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=400)
            
    except Exception as e:
        print(f"Error handling reorder_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)