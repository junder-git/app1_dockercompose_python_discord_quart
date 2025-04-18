"""
handle_add_to_queue method for Discord bot
Handles API requests for adding tracks to the queue
"""
from aiohttp import web

async def handle_add_to_queue(self, request):
    """
    Handle adding a track to the queue
    
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
        video_id = data.get('video_id')
        video_title = data.get('video_title', 'Unknown title')
        
        if not all([guild_id, channel_id, video_id]):
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Use the shared add_to_queue method
        result = await self.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=500)
            
    except Exception as e:
        print(f"Error handling add_to_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)