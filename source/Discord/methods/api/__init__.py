"""
API handler methods for Discord bot
Methods for handling API requests from external services
"""
from .start_api_server import start_api_server
from .handle_join import handle_join
from .handle_guild_count import handle_guild_count
from .handle_guild_ids import handle_guild_ids
from .handle_add_to_queue import handle_add_to_queue
from .handle_get_queue import handle_get_queue
from .handle_skip import handle_skip
from .handle_pause import handle_pause
from .handle_resume import handle_resume
from .handle_disconnect import handle_disconnect
from .handle_get_user_voice_state import handle_get_user_voice_state
from .handle_clear_queue import handle_clear_queue
from .handle_shuffle_queue import handle_shuffle_queue
from .handle_reorder_queue import handle_reorder_queue

__all__ = [
    'start_api_server',
    'handle_join',
    'handle_guild_count',
    'handle_guild_ids',
    'handle_add_to_queue',
    'handle_get_queue',
    'handle_skip',
    'handle_pause',
    'handle_resume',
    'handle_disconnect',
    'handle_get_user_voice_state',
    'handle_clear_queue',
    'handle_shuffle_queue',
    'handle_reorder_queue'
]

def apply_methods(bot_class):
    """Apply all API handler methods to the bot class"""
    # Make sure start_api_server is applied first
    bot_class.start_api_server = start_api_server
    bot_class.handle_join = handle_join
    bot_class.handle_guild_count = handle_guild_count
    bot_class.handle_guild_ids = handle_guild_ids
    bot_class.handle_add_to_queue = handle_add_to_queue
    bot_class.handle_get_queue = handle_get_queue
    bot_class.handle_skip = handle_skip
    bot_class.handle_pause = handle_pause
    bot_class.handle_resume = handle_resume
    bot_class.handle_disconnect = handle_disconnect
    bot_class.handle_get_user_voice_state = handle_get_user_voice_state
    bot_class.handle_clear_queue = handle_clear_queue
    bot_class.handle_shuffle_queue = handle_shuffle_queue
    bot_class.handle_reorder_queue = handle_reorder_queue
    return bot_class