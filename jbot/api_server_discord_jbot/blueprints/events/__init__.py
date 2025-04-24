"""
Events Blueprint for Discord Bot
Handles Discord event callbacks
"""
import types
from .on_ready import on_ready

def apply(bot):
    """
    Apply events blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Register event handlers
    bot.on_ready = types.MethodType(on_ready, bot)