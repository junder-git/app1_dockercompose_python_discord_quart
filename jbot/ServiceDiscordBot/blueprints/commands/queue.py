"""
Queue command and functionality for Discord bot
Includes core queue management functions (display, clear, shuffle, reorder)
"""
import discord
from discord.ext import commands
import asyncio
import random

@commands.command(name="queue", aliases=["q"])
async def queue_command(ctx):
    """
    Show the current music queue.
    
    Usage:
    !queue
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    # Check if bot is in a voice channel in this guild
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        message = await ctx.send("I'm not currently in a voice channel.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Get queue ID
    channel_id = str(voice_client.channel.id)
    queue_id = ctx.bot.get_queue_id(str(ctx.guild.id), channel_id)
    
    # Get current queue and currently playing track
    queue = ctx.bot.music_queues[queue_id]
    current_track = ctx.bot.currently_playing.get(queue_id)
    
    # Create embed for the queue
    embed = discord.Embed(
        title="Music Queue",
        description=f"Connected to **{voice_client.channel.name}**",
        color=discord.Color.blue()
    )
    
    # Add currently playing info
    if current_track:
        embed.add_field(
            name="Now Playing",
            value=f"[{current_track['title']}](https://www.youtube.com/watch?v={current_track['id']})",
            inline=False
        )
    
    # Add queue info
    if queue:
        # Build queue text
        queue_text = ""
        for i, track in enumerate(queue[:10]):
            queue_text += f"{i+1}. [{track['title']}](https://www.youtube.com/watch?v={track['id']})\n"
        
        if len(queue) > 10:
            queue_text += f"\n... and {len(queue) - 10} more"
            
        embed.add_field(name="Queue", value=queue_text, inline=False)
        embed.set_footer(text=f"Total tracks in queue: {len(queue)}")
    else:
        embed.add_field(name="Queue", value="No tracks in queue.", inline=False)
    
    # Send response
    message = await ctx.send(embed=embed)
    
    # Don't delete the queue message - it's useful information


@commands.command(name="clearqueue", aliases=["cq"])
async def clear_command(ctx):
    """
    Clear the music queue.
    
    Usage:
    !clear
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
    
    # Clear the queue
    result = await clear_queue(ctx.bot, str(ctx.guild.id), channel_id)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


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
    result = await shuffle_queue(ctx.bot, str(ctx.guild.id), channel_id)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


@commands.command(name="move")
async def move_command(ctx, old_pos: int = None, new_pos: int = None):
    """
    Move a track in the queue to a new position.
    
    Usage:
    !move <old_position> <new_position>
    
    Example:
    !move 3 1
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    if old_pos is None or new_pos is None:
        message = await ctx.send("Please provide both positions. Example: `!move 3 1`")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Convert to 0-based indices
    old_index = old_pos - 1
    new_index = new_pos - 1
    
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
    
    # Reorder the queue
    result = await reorder_queue(ctx.bot, str(ctx.guild.id), channel_id, old_index, new_index)
    
    # Send response
    message = await ctx.send(result["message"])
    await message.delete(delay=ctx.bot.cleartimer)


# Core queue functionality - can be called by API handlers or commands

async def clear_queue(bot, guild_id, channel_id=None):
    """
    Clear queue(s) for a guild, optionally for a specific channel
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str, optional): Discord channel ID. If not provided, all queues for the guild are cleared.
        
    Returns:
        dict: Result containing success status and message
    """
    queues_cleared = 0
    channel_ids = []
    
    if channel_id:
        # Clear a specific queue
        queue_id = bot.get_queue_id(guild_id, channel_id)
        bot.music_queues[queue_id] = []
        bot.currently_playing.pop(queue_id, None)
        channel_ids.append(channel_id)
        queues_cleared = 1
    else:
        # Clear all queues for this guild
        for queue_id in list(bot.music_queues.keys()):
            if queue_id.startswith(f"{guild_id}_"):
                bot.music_queues[queue_id] = []
                bot.currently_playing.pop(queue_id, None)
                this_channel_id = queue_id.split('_')[1]
                channel_ids.append(this_channel_id)
                queues_cleared += 1
    
    # Update control panels
    for ch_id in channel_ids:
        await bot.update_control_panel(guild_id, ch_id)
    
    return {
        "success": True,
        "message": f"Cleared {queues_cleared} queue(s) for guild {guild_id}"
    }


async def shuffle_queue(bot, guild_id, channel_id):
    """
    Shuffle the queue
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    queue_id = bot.get_queue_id(guild_id, channel_id)
    
    if not bot.music_queues[queue_id]:
        return {"success": False, "message": "Queue is empty, nothing to shuffle"}
    
    random.shuffle(bot.music_queues[queue_id])
    
    # Update control panels
    await bot.update_control_panel(guild_id, channel_id)
    
    return {"success": True, "message": "🔀 Queue shuffled"}


async def reorder_queue(bot, guild_id, channel_id, old_index, new_index):
    """
    Move a track in the queue from old_index to new_index
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        old_index (int): Current position of the track
        new_index (int): New position for the track
        
    Returns:
        dict: Result containing success status and message
    """
    queue_id = bot.get_queue_id(guild_id, channel_id)
    
    # Make sure indices are valid
    if not bot.music_queues[queue_id] or old_index < 0 or old_index >= len(bot.music_queues[queue_id]) or \
    new_index < 0 or new_index >= len(bot.music_queues[queue_id]):
        return {"success": False, "message": "Invalid index"}
    
    # Move the track from old_index to new_index
    track = bot.music_queues[queue_id].pop(old_index)
    bot.music_queues[queue_id].insert(new_index, track)
    
    # Update control panels
    await bot.update_control_panel(guild_id, channel_id)
    
    return {
        "success": True,
        "message": f"Track moved from position {old_index+1} to {new_index+1}"
    }