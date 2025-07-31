"""
API Blueprint for Discord Bot
Handles API server setup and API endpoints
"""
import types
from .server import start_api_server, setup_hook
from .handlers import get_api_handlers

def apply(bot):
    """
    Apply API blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Attach server methods
    bot.start_api_server = types.MethodType(start_api_server, bot)
    bot.setup_hook = types.MethodType(setup_hook, bot)
    
    # Register all API handler methods
    for handler_name, handler_func in get_api_handlers().items():
        setattr(bot, handler_name, types.MethodType(handler_func, bot))