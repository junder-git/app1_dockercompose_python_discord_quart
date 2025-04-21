"""
Guild-related API methods for the Discord Bot API client
"""
from .get_guild_count import get_guild_count
from .get_guild_ids import get_guild_ids

class GuildMethods:
    """
    Guild information methods mixin for DiscordBotAPI
    
    These methods retrieve information about Discord guilds (servers)
    """
    get_guild_count = get_guild_count
    get_guild_ids = get_guild_ids

__all__ = ['GuildMethods']