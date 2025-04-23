"""
Handler for guild count API requests
"""
from aiohttp import web

async def handle_guild_count(self, request):
    """
    Handle guild count requests
    
    Args:
        request: The aiohttp request object
        
    Returns:
        web.Response: JSON response with guild count or error
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    return web.json_response({"count": len(self.guilds)})