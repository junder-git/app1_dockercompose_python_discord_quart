"""
Playback control methods for Discord bot
Methods for controlling music playback
"""
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
    """Apply all playback control methods to the bot class"""
    bot_class.play_next = play_next
    bot_class.toggle_playback = toggle_playback
    bot_class.skip_track = skip_track
    bot_class.stop_playback = stop_playback
    return bot_class