"""
Playback control methods for the Discord Bot API client
"""
from .skip_track import skip_track
from .pause_playback import pause_playback
from .resume_playback import resume_playback

class PlaybackMethods:
    """
    Playback control methods mixin for DiscordBotAPI
    
    These methods handle music playback operations
    """
    skip_track = skip_track
    pause_playback = pause_playback
    resume_playback = resume_playback

__all__ = ['PlaybackMethods']