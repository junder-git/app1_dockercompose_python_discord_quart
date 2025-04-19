"""
Queue management methods for the Discord Bot API client
"""
from .add_to_queue import add_to_queue
from .get_queue import get_queue
from .clear_queue import clear_queue
from .shuffle_queue import shuffle_queue
from .add_multiple_to_queue import add_multiple_to_queue
from .reorder_queue import reorder_queue

class QueueMethods:
    """
    Queue management methods mixin for DiscordBotAPI
    
    These methods handle music queue operations
    """
    add_to_queue = add_to_queue
    get_queue = get_queue
    clear_queue = clear_queue
    shuffle_queue = shuffle_queue
    add_multiple_to_queue = add_multiple_to_queue
    reorder_queue = reorder_queue

__all__ = ['QueueMethods']