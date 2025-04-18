"""
Playback control methods for Discord bot
Methods for controlling music playback
"""
import types
from .play_next import play_next
from .toggle_playback import toggle_playback
from .skip_track import skip_track
from .stop_playback import stop_playback

__all__ = [
    'play_next',
    'toggle_playback',
    'skip_track',
    'stop_playback'
]

def apply_methods(bot_class):
    """
    Apply all playback control methods to the bot class
    
    This uses types.MethodType to properly bind the functions as methods to the bot instance,
    ensuring they receive 'self' when called.
    """
    bot_class.play_next = types.MethodType(play_next, bot_class)
    bot_class.toggle_playback = types.MethodType(toggle_playback, bot_class)
    bot_class.skip_track = types.MethodType(skip_track, bot_class)
    bot_class.stop_playback = types.MethodType(stop_playback, bot_class)
    return bot_class