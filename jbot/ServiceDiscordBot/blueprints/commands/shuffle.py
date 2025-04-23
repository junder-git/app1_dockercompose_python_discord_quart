"""
Shuffle command for Discord bot
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="shuffle")
async def shuffle_command(ctx):
    """
    Shuffle the current music queue.
    
    Usage:
    !shuffle
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
    
    # Shuffle the queue
    result = await ctx.bot.shuffle_queue(str(ctx.guild.id), channel_id)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)