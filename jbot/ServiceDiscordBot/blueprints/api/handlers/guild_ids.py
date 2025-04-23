"""
Handler for guild IDs API requests
"""
from aiohttp import web

async def handle_guild_ids(self, request):
    """
    Handle guild IDs requests
    
    Args:
        request: The aiohttp request object
        
    Returns:
        web.Response: JSON response with guild IDs or error
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    guild_ids = [str(guild.id) for guild in self.guilds]
    return web.json_response({"guild_ids": guild_ids})