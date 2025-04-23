"""
Leave command for Discord bot - includes voice disconnection functionality
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="leave", aliases=["l", "disconnect"])
async def leave_command(ctx):
    """
    Make the bot leave the voice channel.
    
    Usage:
    !leave
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    # Check if bot is in a voice channel in this guild
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        message = await ctx.send("I'm not currently in a voice channel.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Check if user is in the same voice channel
    if not ctx.author.voice or ctx.author.voice.channel != voice_client.channel:
        message = await ctx.send("You need to be in the same voice channel to use this command.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Get the channel ID for the voice client
    channel_id = str(voice_client.channel.id)
    
    # Disconnect from voice channel
    result = await disconnect_from_voice(ctx.bot, str(ctx.guild.id), channel_id, preserve_queue=False)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


# Core voice disconnection functionality - can be called by API handlers or commands

async def disconnect_from_voice(bot, guild_id, channel_id=None, preserve_queue=True):
    """
    Disconnect from voice channel with option to clear the queue
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str, optional): Discord channel ID. If not provided, disconnects from all channels in the guild.
        preserve_queue (bool, optional): Whether to preserve the queue after disconnecting
        
    Returns:
        dict: Result containing success status and message
    """
    if channel_id:
        # Disconnect from a specific channel
        queue_id = bot.get_queue_id(guild_id, channel_id)
        
        if queue_id in bot.voice_connections and bot.voice_connections[queue_id].is_connected():
            # If preserving queue and there's a current track, save it
            if preserve_queue and queue_id in bot.currently_playing:
                current_track = bot.currently_playing.get(queue_id)
                if current_track:
                    # Add current track back to the front of the queue
                    bot.music_queues[queue_id].insert(0, current_track)
            else:
                # If not preserving queue, clear it
                bot.music_queues[queue_id] = []
            
            # Always clear the currently playing track
            bot.currently_playing.pop(queue_id, None)
            
            await bot.voice_connections[queue_id].disconnect(force=True)
            bot.voice_connections.pop(queue_id, None)
            
            message = "Disconnected from voice channel"
            if not preserve_queue:
                message += " and cleared queue"
            
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": f"Not connected to voice channel {channel_id} in guild {guild_id}"}
    
    # If no specific channel_id, disconnect from any voice connection in this guild
    for queue_id, voice_client in list(bot.voice_connections.items()):
        if queue_id.startswith(f"{guild_id}_") and voice_client.is_connected():
            # Extract channel_id from queue_id
            disconnected_channel_id = queue_id.split('_')[1]
            
            # If preserving queue and there's a current track, save it
            if preserve_queue and queue_id in bot.currently_playing:
                current_track = bot.currently_playing.get(queue_id)
                if current_track:
                    # Add current track back to the front of the queue
                    bot.music_queues[queue_id].insert(0, current_track)
            else:
                # If not preserving queue, clear it
                bot.music_queues[queue_id] = []
            
            # Always clear the currently playing track
            bot.currently_playing.pop(queue_id, None)
            
            await voice_client.disconnect(force=True)
            bot.voice_connections.pop(queue_id, None)
            
            message = "Disconnected from voice channel"
            if not preserve_queue:
                message += " and cleared queue"
            
            await bot.update_control_panel(guild_id, disconnected_channel_id)
            
            return {"success": True, "message": message}
    
    return {"success": False, "message": "Not connected to any voice channel in this guild"}