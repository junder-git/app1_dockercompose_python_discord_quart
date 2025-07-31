"""
Methods module for Discord API client
"""
from .guild import GuildMethods
from .voice import VoiceMethods
from .queue import QueueMethods
from .playback import PlaybackMethods
from .user import UserMethods

__all__ = [
    'GuildMethods',
    'VoiceMethods',
    'QueueMethods',
    'PlaybackMethods',
    'UserMethods'
]