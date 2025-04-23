"""
Join command for Discord bot - includes voice channel connection functionality
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="join", aliases=["j"])
async def join_command(ctx):
    """
    Make the bot join your voice channel.
    
    Usage:
    !join
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    # Check if user is in a voice channel
    if not ctx.author.voice:
        message = await ctx.send("You need to be in a voice channel to use this command.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Join the voice channel and show controls
    await ctx.bot.join_and_show_controls(ctx.channel, voice_channel, ctx.guild.id)


# Core voice functionality - can be called by API handlers or commands

async def get_voice_client(bot, guild_id, channel_id, connect=False):
    """
    Get or create a voice client for the specified channel
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        connect (bool, optional): Whether to connect if not already connected
        
    Returns:
        tuple: (voice_client, queue_id) tuple
    """
    queue_id = bot.get_queue_id(guild_id, channel_id)
    
    # Return existing connection if available
    if queue_id in bot.voice_connections and bot.voice_connections[queue_id].is_connected():
        return bot.voice_connections[queue_id], queue_id
    
    # Connect if requested and not already connected
    if connect:
        guild = bot.get_guild(int(guild_id))
        if not guild:
            return None, queue_id
            
        voice_channel = guild.get_channel(int(channel_id))
        if not voice_channel:
            return None, queue_id
            
        try:
            voice_client = await voice_channel.connect()
            bot.voice_connections[queue_id] = voice_client
            return voice_client, queue_id
        except Exception as e:
            print(f"Error connecting to voice channel: {e}")
            return None, queue_id
    
    return None, queue_id


async def follow_to_voice_channel(bot, guild_id, current_channel_id, new_channel_id, user):
    """
    Follow a user to a new voice channel, preserving the queue and current track
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        current_channel_id (str): Current voice channel ID
        new_channel_id (str): New voice channel ID to move to
        user: Discord user object
        
    Returns:
        dict: Result containing success status and message
    """
    try:
        # Get the current queue ID
        old_queue_id = bot.get_queue_id(guild_id, current_channel_id)
        
        # Get the new queue ID
        new_queue_id = bot.get_queue_id(guild_id, new_channel_id)
        
        # Get the guild
        guild = bot.get_guild(int(guild_id))
        if not guild:
            return {"success": False, "message": "Guild not found"}
        
        # Get the new voice channel
        new_voice_channel = guild.get_channel(int(new_channel_id))
        if not new_voice_channel or not isinstance(new_voice_channel, discord.VoiceChannel):
            return {"success": False, "message": "Voice channel not found"}
        
        # Save current playback state and queue
        current_track = bot.currently_playing.get(old_queue_id)
        was_playing = False
        was_paused = False
        
        # Check if we were connected and playing/paused
        if old_queue_id in bot.voice_connections and bot.voice_connections[old_queue_id].is_connected():
            voice_client = bot.voice_connections[old_queue_id]
            was_playing = voice_client.is_playing()
            was_paused = voice_client.is_paused()
            
            # Stop current playback if any
            if was_playing or was_paused:
                voice_client.stop()
            
            # Disconnect from the current voice channel
            await voice_client.disconnect(force=True)
            bot.voice_connections.pop(old_queue_id, None)
        
        # Connect to the new voice channel
        try:
            new_voice_client = await new_voice_channel.connect()
            bot.voice_connections[new_queue_id] = new_voice_client
        except Exception as e:
            print(f"Error connecting to new voice channel: {e}")
            return {"success": False, "message": f"Failed to connect to new voice channel: {str(e)}"}
        
        # Transfer queue from old to new channel
        bot.music_queues[new_queue_id] = bot.music_queues.pop(old_queue_id, [])
        
        # Set the interruption flag to stop any ongoing playlist processing
        bot.playlist_processing[old_queue_id] = True
        
        # Update queue IDs in any ongoing operations
        bot.playlist_processing[new_queue_id] = bot.playlist_processing.pop(old_queue_id, False)
        
        # If we had a current track, add it back to the front of the queue to resume
        if current_track and (was_playing or was_paused):
            bot.music_queues[new_queue_id].insert(0, current_track)
            # Clear the currently playing track for the old queue
            bot.currently_playing.pop(old_queue_id, None)
            
            # Import play_next from the play command if needed
            from .play import play_next
            
            # Immediately start playback if we were playing
            if was_playing:
                asyncio.create_task(play_next(bot, guild_id, new_channel_id))
        
        # Update all control panels
        for text_channel_id, message_id in list(bot.control_panels.items()):
            try:
                text_channel = guild.get_channel(text_channel_id)
                if text_channel:
                    await bot.update_control_panel(guild_id, new_channel_id)
            except Exception as e:
                print(f"Error updating control panel: {e}")
        
        return {
            "success": True,
            "message": f"Followed {user.display_name} to {new_voice_channel.name}"
        }
        
    except Exception as e:
        print(f"Error following to voice channel: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}


async def check_same_voice_channel(bot, user, channel_id):
    """
    Check if a user is in the specified voice channel
    
    Args:
        bot: The Discord bot instance
        user: Discord user object
        channel_id (str): Discord channel ID
        
    Returns:
        bool: True if user is in the specified channel, False otherwise
    """
    return user.voice and str(user.voice.channel.id) == channel_id