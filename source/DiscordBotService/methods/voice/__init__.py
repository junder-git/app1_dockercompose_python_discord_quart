"""
Voice connection methods for Discord bot
Methods for managing voice channel connections
"""
import types
from .get_voice_client import get_voice_client
from .disconnect_from_voice import disconnect_from_voice
from .follow_to_voice_channel import follow_to_voice_channel
from .check_same_voice_channel import check_same_voice_channel

__all__ = [
    'get_voice_client',
    'disconnect_from_voice',
    'follow_to_voice_channel',
    'check_same_voice_channel'
]

def apply_methods(bot_class):
    """
    Apply all voice connection methods to the bot class
    
    This uses types.MethodType to properly bind the functions as methods to the bot instance,
    ensuring they receive 'self' when called.
    """
    bot_class.get_voice_client = types.MethodType(get_voice_client, bot_class)
    bot_class.disconnect_from_voice = types.MethodType(disconnect_from_voice, bot_class)
    bot_class.follow_to_voice_channel = types.MethodType(follow_to_voice_channel, bot_class)
    bot_class.check_same_voice_channel = types.MethodType(check_same_voice_channel, bot_class)
    return bot_class