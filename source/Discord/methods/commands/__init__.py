"""
Command handler methods for Discord bot
Methods for handling explicit Discord commands
"""
from .hello import hello
from .help_command import help_command
from .search_command import search_command

__all__ = [
    'hello',
    'help_command',
    'search_command'
]

def apply_methods(bot_class):
    """
    Apply all command methods to the bot class
    Note: These methods are typically decorated with @bot.command()
    so they are not directly attached to the bot class
    """
    # Since commands are registered with decorators, we don't need to
    # explicitly attach them to the bot class
    # However, we can store them as attributes for reference
    bot_class._hello_command = hello
    bot_class._help_command = help_command
    bot_class._search_command = search_command
    return bot_class