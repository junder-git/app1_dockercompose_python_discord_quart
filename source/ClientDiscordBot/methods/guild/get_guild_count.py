"""
Method to get the count of guilds the bot is in
"""

async def get_guild_count(self):
    """
    Get the count of guilds the bot is in
    
    Returns:
        int: Number of guilds
    """
    result = await self._get_request("guild_count")
    return result.get("count", 0)