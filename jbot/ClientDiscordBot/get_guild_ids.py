"""
Get the IDs of all guilds the bot is in
"""
from .get_request import get_request

async def get_guild_ids(base_url, secret_key, session):
    result = await get_request(base_url, secret_key, session, "guild_ids")
    return result.get("guild_ids", [])