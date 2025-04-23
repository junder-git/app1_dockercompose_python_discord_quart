"""
Pause command for Discord bot
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="pause")
async def pause_command(ctx):
    """
    Pause the currently playing song.
    
    Usage:
    !pause
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
    
    # Check if bot is playing
    if not voice_client.is_playing():
        message = await ctx.send("Nothing is currently playing.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Use toggle_playback method
    result = await toggle_playback(ctx.bot, str(ctx.guild.id), str(ctx.author.voice.channel.id))
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


async def toggle_playback(bot, guild_id, channel_id):
    """
    Toggle playback between pause and resume
    
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
    
    if voice_client.is_playing():
        # Pause if currently playing
        voice_client.pause()
        
        # Update control panels
        await bot.update_control_panel(guild_id, channel_id)
        
        return {"success": True, "message": "⏸️ Paused playback"}
    elif voice_client.is_paused():
        # Resume if currently paused
        voice_client.resume()
        
        # Update control panels
        await bot.update_control_panel(guild_id, channel_id)
        
        return {"success": True, "message": "▶️ Resumed playback"}
    else:
        return {"success": False, "message": "Nothing is playing to pause or resume"}