"""
UI methods for Discord bot
Methods for handling Discord UI elements and control panels
"""
import types
from .join_and_show_controls import join_and_show_controls
from .send_control_panel import send_control_panel
from .update_control_panel import update_control_panel

__all__ = [
    'join_and_show_controls',
    'send_control_panel',
    'update_control_panel'
]

def apply_methods(bot_class):
    """
    Apply all UI methods to the bot class
    
    This uses types.MethodType to properly bind the functions as methods to the bot instance,
    ensuring they receive 'self' when called.
    """
    bot_class.join_and_show_controls = types.MethodType(join_and_show_controls, bot_class)
    bot_class.send_control_panel = types.MethodType(send_control_panel, bot_class)
    bot_class.update_control_panel = types.MethodType(update_control_panel, bot_class)
    return bot_class