"""
Search command for Discord bot
"""
import discord
from discord.ext import commands
import asyncio
from .play import play_next

@commands.command(name="search", aliases=["find"])
async def search_command(ctx, *, query=None):
    """
    Search for a song on YouTube.
    
    Usage:
    !search <search query>
    
    Example:
    !search never gonna give you up
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    # Check if user is in a voice channel
    if not ctx.author.voice:
        message = await ctx.send("You need to be in a voice channel to use this command.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    # Check if a query was provided
    if not query:
        message = await ctx.send("Please provide a search query. Example: `!search never gonna give you up`")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Join the voice channel if not already connected
    await ctx.bot.join_and_show_controls(ctx.channel, voice_channel, ctx.guild.id)
    
    # Send searching message
    search_msg = await ctx.send(f"🔍 Searching for: **{query}**")
    
    try:
        # Search for videos
        search_results = await ctx.bot.youtube_client.search_videos(query)
        
        if not search_results:
            await search_msg.edit(content=f"❌ No results found for: **{query}**")
            await search_msg.delete(delay=ctx.bot.cleartimer)
            return
        
        # Create embed for results
        embed = discord.Embed(
            title=f"Search Results for: {query}",
            description="Select a track to play",
            color=discord.Color.green()
        )
        
        # Add results to embed
        for i, result in enumerate(search_results[:5]):
            # Get duration
            duration = result.get('duration')
            if duration:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            embed.add_field(
                name=f"{i+1}. {result['title']}",
                value=f"Duration: {duration_str}",
                inline=False
            )
        
        # Delete search message
        await search_msg.delete()
        
        # Create select menu for choosing tracks
        select = discord.ui.Select(
            placeholder="Choose a track",
            min_values=1,
            max_values=1,
            custom_id="search_results"
        )
        
        # Add options to select menu
        for i, result in enumerate(search_results[:5]):
            # Truncate title if needed
            title = result['title']
            if len(title) > 100:
                title = title[:97] + "..."
                
            # Get duration
            duration = result.get('duration')
            if duration:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            select.add_option(
                label=f"{i+1}. {title[:80]}",  # Discord limits labels to 100 chars
                value=f"{result['id']}",
                description=f"Duration: {duration_str}"
            )
        
        # Create view and add select
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        
        # Define select callback
        async def select_callback(interaction):
            # Only allow the original command user to select
            if interaction.user != ctx.author:
                await interaction.response.send_message(
                    "Only the person who used the search command can select a track.",
                    ephemeral=True
                )
                return
                
            # Get the selected track ID
            video_id = interaction.data['values'][0]
            
            # Find the selected track
            selected_track = None
            for result in search_results:
                if result['id'] == video_id:
                    selected_track = result
                    break
            
            if not selected_track:
                await interaction.response.send_message(
                    "Error: Could not find the selected track.",
                    ephemeral=True
                )
                return
            
            # Acknowledge the interaction
            await interaction.response.defer(ephemeral=True)
            
            # Add track to queue
            result = await ctx.bot.add_to_queue(
                str(ctx.guild.id),
                str(voice_channel.id),
                selected_track['id'],
                selected_track['title']
            )
            
            if result["success"]:
                # Confirm selection
                confirm_msg = await interaction.followup.send(
                    f"Added to queue: **{selected_track['title']}**",
                    ephemeral=True
                )
                # Delete original search results message
                try:
                    await results_message.delete()
                except:
                    pass
            else:
                await interaction.followup.send(
                    f"Failed to add track: {result['message']}",
                    ephemeral=True
                )
        
        # Set callback
        select.callback = select_callback
        
        # Send results
        results_message = await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        print(f"Error searching for videos: {e}")
        error_msg = await ctx.send(f"An error occurred while searching: {str(e)}")
        await error_msg.delete(delay=ctx.bot.cleartimer)

# Core add_to_queue functionality - can be called by API handlers or commands
async def add_to_queue(bot, guild_id, channel_id, video_id, video_title):
    """
    Add a track to the queue and start playing if needed
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        video_id (str): YouTube video ID
        video_title (str): YouTube video title
        
    Returns:
        dict: Result containing success status, message, and queue length
    """
    voice_client, queue_id = await bot.get_voice_client(guild_id, channel_id, connect=True)
    
    if not voice_client:
        return {"success": False, "message": "Could not connect to voice channel"}
    
    # Add to queue
    bot.music_queues[queue_id].append({
        "id": video_id,
        "title": video_title,
        "url": f"https://www.youtube.com/watch?v={video_id}"
    })
    
    # If we're not playing anything in this queue, start playing
    if queue_id not in bot.currently_playing:
        asyncio.create_task(play_next(bot, guild_id, channel_id))
    
    # Update control panels
    await bot.update_control_panel(guild_id, channel_id)
    
    return {
        "success": True, 
        "message": f"Added to queue: {video_title}",
        "queue_length": len(bot.music_queues[queue_id])
    }
