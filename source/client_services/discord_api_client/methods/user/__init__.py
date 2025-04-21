"""
User-related API methods for the Discord Bot API client
"""
from .get_user_voice_state import get_user_voice_state

class UserMethods:
    """
    User state methods mixin for DiscordBotAPI
    
    These methods handle user state information
    """
    get_user_voice_state = get_user_voice_state

__all__ = ['UserMethods']