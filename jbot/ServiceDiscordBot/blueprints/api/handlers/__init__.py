"""
API Handler methods for Discord Bot
"""
from .guild_count import handle_guild_count
from .guild_ids import handle_guild_ids
from .add_to_queue import handle_add_to_queue
from .get_queue import handle_get_queue
from .clear_queue import handle_clear_queue
from .shuffle_queue import handle_shuffle_queue
from .reorder_queue import handle_reorder_queue
from .skip import handle_skip
from .pause import handle_pause
from .resume import handle_resume
from .join import handle_join
from .disconnect import handle_disconnect
from .get_user_voice_state import handle_get_user_voice_state

def get_api_handlers():
    """
    Get all API handler methods
    
    Returns:
        dict: Dictionary of handler names to handler functions
    """
    return {
        'handle_guild_count': handle_guild_count,
        'handle_guild_ids': handle_guild_ids,
        'handle_add_to_queue': handle_add_to_queue,
        'handle_get_queue': handle_get_queue,
        'handle_clear_queue': handle_clear_queue,
        'handle_shuffle_queue': handle_shuffle_queue,
        'handle_reorder_queue': handle_reorder_queue,
        'handle_skip': handle_skip,
        'handle_pause': handle_pause,
        'handle_resume': handle_resume,
        'handle_join': handle_join,
        'handle_disconnect': handle_disconnect,
        'handle_get_user_voice_state': handle_get_user_voice_state,
    }