"""
Commands Blueprint for Discord Bot
Handles Discord slash commands and message commands
"""
import discord
from discord.ext import commands

def apply(bot):
    """
    Apply commands blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Register all command handlers
    register_commands(bot)
    
def register_commands(bot):
    """
    Register all commands with the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Music commands
    from .play import play_command
    from .join import join_command
    from .leave import leave_command
    from .pause import pause_command
    from .resume import resume_command
    from .skip import skip_command
    from .stop import stop_command
    from .queue import queue_command
    from .shuffle import shuffle_command
    from .search import search_command
    
    # Register commands with the bot
    bot.add_command(play_command)
    bot.add_command(join_command)
    bot.add_command(leave_command)
    bot.add_command(pause_command)
    bot.add_command(resume_command)
    bot.add_command(skip_command)
    bot.add_command(stop_command)
    bot.add_command(queue_command)
    bot.add_command(shuffle_command)
    bot.add_command(search_command)