"""
Queue methods for Discord bot
Methods related to queue management
"""
import types
from .get_queue_id import get_queue_id
from .add_to_queue import add_to_queue
from .reorder_queue import reorder_queue
from .clear_queue import clear_queue
from .shuffle_queue import shuffle_queue

__all__ = [
    'get_queue_id',
    'add_to_queue',
    'reorder_queue',
    'clear_queue',
    'shuffle_queue'
]

def apply_methods(bot_class):
    """
    Apply all queue methods to the bot class
    
    This uses types.MethodType to properly bind the functions as methods to the bot instance,
    ensuring they receive 'self' when called.
    """
    bot_class.get_queue_id = types.MethodType(get_queue_id, bot_class)
    bot_class.add_to_queue = types.MethodType(add_to_queue, bot_class)
    bot_class.reorder_queue = types.MethodType(reorder_queue, bot_class)
    bot_class.clear_queue = types.MethodType(clear_queue, bot_class)
    bot_class.shuffle_queue = types.MethodType(shuffle_queue, bot_class)
    return bot_class