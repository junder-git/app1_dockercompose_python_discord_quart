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
    from .play import play_command, play_next
    from .join import join_command, get_voice_client, follow_to_voice_channel, check_same_voice_channel
    from .leave import leave_command, disconnect_from_voice
    from .pause import pause_command, toggle_playback
    from .resume import resume_command
    from .skip import skip_command, skip_track
    from .stop import stop_command, stop_playback
    from .queue import queue_command, clear_command, shuffle_command, move_command, clear_queue, shuffle_queue, reorder_queue
    from .search import search_command, add_to_queue
    
    # Register commands with the bot
    bot.add_command(play_command)
    bot.add_command(play_next)
    bot.add_command(join_command)
    bot.add_command(get_voice_client)
    bot.add_command(follow_to_voice_channel)
    bot.add_command(check_same_voice_channel)
    bot.add_command(leave_command)
    bot.add_command(disconnect_from_voice)
    bot.add_command(pause_command)
    bot.add_command(toggle_playback)
    bot.add_command(resume_command)
    bot.add_command(skip_command)
    bot.add_command(skip_track)
    bot.add_command(stop_command)
    bot.add_command(stop_playback)
    bot.add_command(queue_command)
    bot.add_command(clear_command)
    bot.add_command(shuffle_command)
    bot.add_command(move_command)
    bot.add_command(clear_queue)
    bot.add_command(shuffle_queue)
    bot.add_command(reorder_queue)
    bot.add_command(search_command)
    bot.add_command(add_to_queue)