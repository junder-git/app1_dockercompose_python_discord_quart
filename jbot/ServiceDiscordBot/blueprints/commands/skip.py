"""
Skip command for Discord bot - includes core skip functionality
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="skip", aliases=["s", "next"])
async def skip_command(ctx):
    """
    Skip the currently playing song.
    
    Usage:
    !skip
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
    
    # Check if bot is playing or paused
    if not voice_client.is_playing() and not voice_client.is_paused():
        message = await ctx.send("Nothing is currently playing to skip.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
        
    # Skip current track
    channel_id = str(voice_client.channel.id)
    result = await skip_track(ctx.bot, str(ctx.guild.id), channel_id)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


# Core skip functionality - can be called by API handlers or commands
async def skip_track(bot, guild_id, channel_id):
    """
    Skip the current track
    
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
    
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        return {"success": True, "message": "⏭️ Skipped to next track"}
    else:
        return {"success": False, "message": "Nothing is playing to skip"}