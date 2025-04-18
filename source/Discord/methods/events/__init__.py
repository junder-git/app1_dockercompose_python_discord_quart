"""
Event handler methods for Discord bot
Methods for handling Discord events
"""
from .setup_hook import setup_hook
from .on_ready import on_ready
from .on_message import on_message

__all__ = [
    'setup_hook',
    'on_ready',
    'on_message'
]

def apply_methods(bot_class):
    """Apply all event handler methods to the bot class"""
    bot_class.setup_hook = setup_hook
    bot_class.on_ready = on_ready
    bot_class.on_message = on_message
    return bot_class