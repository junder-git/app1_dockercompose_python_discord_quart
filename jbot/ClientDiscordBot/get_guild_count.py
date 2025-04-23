"""
Get the count of guilds the bot is in
"""
from .get_request import get_request

async def get_guild_count(base_url, secret_key, session):
    result = await get_request(base_url, secret_key, session, "guild_count")
    return result.get("count", 0)