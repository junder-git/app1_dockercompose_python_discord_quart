"""
Queue methods for Discord bot
Methods related to queue management
"""
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
    """Apply all queue methods to the bot class"""
    bot_class.get_queue_id = get_queue_id
    bot_class.add_to_queue = add_to_queue
    bot_class.reorder_queue = reorder_queue
    bot_class.clear_queue = clear_queue
    bot_class.shuffle_queue = shuffle_queue
    return bot_class