"""
Method to get the IDs of all guilds the bot is in
"""

async def get_guild_ids(self):
    """
    Get the IDs of all guilds the bot is in
    
    Returns:
        list: List of guild IDs
    """
    result = await self._get_request("guild_ids")
    return result.get("guild_ids", [])