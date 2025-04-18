"""
handle_guild_ids method for Discord bot
Handles API requests for guild IDs list
"""
from aiohttp import web

async def handle_guild_ids(self, request):
    """
    Handle guild IDs requests
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with list of guild IDs
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    guild_ids = [str(guild.id) for guild in self.guilds]
    return web.json_response({"guild_ids": guild_ids})