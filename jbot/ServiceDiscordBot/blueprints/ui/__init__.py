"""
UI Blueprint for Discord Bot
Handles UI components and controls
"""
import types
from .join_and_show_controls import join_and_show_controls
from .update_control_panel import update_control_panel
from .send_control_panel import send_control_panel

# Import components for registration in components module
from .components import register_components

def apply(bot):
    """
    Apply UI blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind UI methods to the bot
    bot.join_and_show_controls = types.MethodType(join_and_show_controls, bot)
    bot.update_control_panel = types.MethodType(update_control_panel, bot)
    bot.send_control_panel = types.MethodType(send_control_panel, bot)
    
    # Register UI components (views, modals, etc.)
    register_components(bot)