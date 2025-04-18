"""
Event handler methods for Discord bot
Methods for handling Discord events
"""
# Don't import setup_hook to avoid trying to replace it
from .on_ready import on_ready
from .on_message import on_message

__all__ = [
    'on_ready',
    'on_message'
]

def apply_methods(bot_class):
    """Apply all event handler methods to the bot class"""
    # Don't replace setup_hook as it's already defined in the MyBot class
    bot_class.on_ready = on_ready
    bot_class.on_message = on_message
    return bot_class