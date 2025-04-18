"""
Methods package for Discord Bot
Imports all methods from all categories
"""
# Import all methods from all categories
from .queue import *
from .voice import *
from .playback import *
from .ui import *
from .api import *
from .events import *
from .commands import *

def apply_methods(bot_class):
    """Apply all methods to the bot class"""
    # Get all methods from all categories
    from .queue import apply_methods as apply_queue_methods
    from .voice import apply_methods as apply_voice_methods
    from .playback import apply_methods as apply_playback_methods
    from .ui import apply_methods as apply_ui_methods
    from .api import apply_methods as apply_api_methods
    from .events import apply_methods as apply_event_methods
    from .commands import apply_methods as apply_command_methods
    
    # Apply all methods to the bot class
    apply_queue_methods(bot_class)
    apply_voice_methods(bot_class)
    apply_playback_methods(bot_class)
    apply_ui_methods(bot_class)
    apply_api_methods(bot_class)
    apply_event_methods(bot_class)
    apply_command_methods(bot_class)
    
    return bot_class