"""
Voice connection methods for the Discord Bot API client
"""
from .join_voice_channel import join_voice_channel
from .disconnect_voice_channel import disconnect_voice_channel

class VoiceMethods:
    """
    Voice connection methods mixin for DiscordBotAPI
    
    These methods handle voice channel connections
    """
    join_voice_channel = join_voice_channel
    disconnect_voice_channel = disconnect_voice_channel

__all__ = ['VoiceMethods']