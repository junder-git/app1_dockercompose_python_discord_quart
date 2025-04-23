"""
Handler for adding a track to the queue API requests - calls the core add_to_queue functionality
"""
from aiohttp import web
from ...commands.search import add_to_queue

async def handle_add_to_queue(self, request):
    """
    Handle adding a track to the queue
    
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
        video_id = data.get('video_id')
        video_title = data.get('video_title', 'Unknown title')
        
        if not all([guild_id, channel_id, video_id]):
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # First, ensure we're connected to the voice channel
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
        
        if not voice_client:
            return web.json_response({"error": "Failed to connect to voice channel"}, status=500)
        
        # Then add the track to the queue using the core functionality
        result = await add_to_queue(self, guild_id, channel_id, video_id, video_title)
        
        if result["success"]:
            return web.json_response(result)
        else:
            return web.json_response({"error": result["message"]}, status=500)
            
    except Exception as e:
        print(f"Error handling add_to_queue request: {e}")
        return web.json_response({"error": str(e)}, status=500)