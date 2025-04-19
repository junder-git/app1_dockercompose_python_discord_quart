"""
Discord API Client Blueprint
Provides a modular interface to communicate with the Discord bot API
"""
from quart import Blueprint

from .core.api_base import DiscordAPIBase
from .methods.guild import GuildMethods
from .methods.voice import VoiceMethods
from .methods.queue import QueueMethods
from .methods.playback import PlaybackMethods
from .methods.user import UserMethods

# Create blueprint
discord_api_client_bp = Blueprint('discord_api_client', __name__)

class DiscordBotAPI(DiscordAPIBase, 
                    GuildMethods,
                    VoiceMethods, 
                    QueueMethods, 
                    PlaybackMethods,
                    UserMethods):
    """
    Discord Bot API Client
    
    This class is composed of multiple mixins that provide specific functionality groups.
    The actual implementation of each method is in its respective module file.
    """
    pass

# Factory function to create API client instance
def create_discord_bot_api(host, port, secret_key):
    """Create and return an instance of the Discord Bot API client"""
    return DiscordBotAPI(host, port, secret_key)