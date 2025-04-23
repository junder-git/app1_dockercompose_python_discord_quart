"""
Stop command for Discord bot - includes stop_playback functionality
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="stop", aliases=["clear"])
async def stop_command(ctx):
    """
    Stop playback and clear the queue.
    
    Usage:
    !stop
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
    
    # Get channel ID
    channel_id = str(voice_client.channel.id)
    
    # Stop playback and clear queue
    result = await stop_playback(ctx.bot, str(ctx.guild.id), channel_id)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


# Core stop_playback functionality - can be called by API handlers or commands
async def stop_playback(bot, guild_id, channel_id):
    """
    Stop playback and clear the queue
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    voice_client, queue_id = await bot.get_voice_client(guild_id, channel_id)
    
    if not voice_client:
        return {"success": False, "message": "Not connected to a voice channel"}
    
    # Set flag to interrupt any ongoing playlist additions
    bot.playlist_processing[queue_id] = True
    
    # Clear queue and stop playing
    bot.music_queues[queue_id] = []
    bot.currently_playing.pop(queue_id, None)
    
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
    
    # Update control panel
    await bot.update_control_panel(guild_id, channel_id)
    
    return {"success": True, "message": "⏹️ Stopped playback and cleared queue"}