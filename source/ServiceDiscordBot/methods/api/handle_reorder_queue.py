"""
handle_reorder_queue method for Discord bot
Handles API requests to reorder tracks in the queue
"""
from aiohttp import web

async def handle_reorder_queue(self, request):
    """
    Handle requests to reorder tracks in the queue
    
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