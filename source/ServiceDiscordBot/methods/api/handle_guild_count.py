"""
handle_guild_count method for Discord bot
Handles API requests for guild count information
"""
from aiohttp import web

async def handle_guild_count(self, request):
    """
    Handle guild count requests
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with guild count
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    return web.json_response({"count": len(self.guilds)})