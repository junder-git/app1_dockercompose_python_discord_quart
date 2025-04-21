"""
Event handler methods for Discord bot
Methods for handling Discord events
"""
import types
from .setup_hook import setup_hook
from .on_ready import on_ready
from .on_message import on_message

__all__ = [
    'setup_hook',
    'on_ready',
    'on_message'
]

def apply_methods(bot_class):
    """
    Apply all event handler methods to the bot class
    
    This uses types.MethodType to properly bind the functions to the bot instance,
    ensuring they receive 'self' when called.
    """
    # For a class instance, we need to use types.MethodType to bind the function as a method
    bot_class.setup_hook = types.MethodType(setup_hook, bot_class)
    bot_class.on_ready = types.MethodType(on_ready, bot_class)
    bot_class.on_message = types.MethodType(on_message, bot_class)
    return bot_class