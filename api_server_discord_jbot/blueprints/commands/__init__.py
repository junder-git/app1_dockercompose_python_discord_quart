"""
Commands Blueprint for Discord Bot
Handles Discord slash commands and message commands
"""
import types
# Music commands
from .play import play_command, play_next
from .join import get_voice_client, follow_to_voice_channel, check_same_voice_channel
from .leave import leave_command, disconnect_from_voice
from .pause import pause_command, toggle_playback
from .resume import resume_command
from .skip import skip_command, skip_track
from .stop import stop_command, stop_playback
from .queue import queue_command, clear_command, shuffle_command, move_command, clear_queue, shuffle_queue, reorder_queue
from .search import search_command, add_to_queue
from .slash_commands import apply_slash_commands

def apply(bot):
    """
    Apply commands blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Register all command handlers
    # Register commands with the bot
    bot.add_command(play_command)
    bot.add_command(leave_command)
    bot.add_command(pause_command)
    bot.add_command(resume_command)
    bot.add_command(skip_command)
    bot.add_command(stop_command)
    bot.add_command(queue_command)
    bot.add_command(clear_command)
    bot.add_command(shuffle_command)
    bot.add_command(move_command)
    bot.add_command(search_command)
    bot.play_next = types.MethodType(play_next, bot)
    bot.get_voice_client = types.MethodType(get_voice_client, bot)
    bot.follow_to_voice_channel = types.MethodType(follow_to_voice_channel, bot)
    bot.check_same_voice_channel = types.MethodType(check_same_voice_channel, bot)
    bot.disconnect_from_voice = types.MethodType(disconnect_from_voice, bot)
    bot.toggle_playback = types.MethodType(toggle_playback, bot)
    bot.skip_track = types.MethodType(skip_track, bot)
    bot.stop_playback = types.MethodType(stop_playback, bot)    
    bot.clear_queue = types.MethodType(clear_queue, bot)
    bot.shuffle_queue = types.MethodType(shuffle_queue, bot)
    bot.reorder_queue = types.MethodType(reorder_queue, bot)
    bot.add_to_queue = types.MethodType(add_to_queue, bot)

    # Apply slash commands
    apply_slash_commands(bot)