"""
Play command for Discord bot - includes play_next functionality
"""
import discord
from discord.ext import commands
import asyncio

@commands.command(name="play", aliases=["p"])
async def play_command(ctx, *, query=None):
    """
    Play a song or add it to the queue.
    
    Usage:
    !play <YouTube URL or search query>
    
    Example:
    !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
    !play never gonna give you up
    """
    # Delete command message after a short delay
    asyncio.create_task(ctx.message.delete(delay=ctx.bot.cleartimer))
    
    # Check if user is in a voice channel
    if not ctx.author.voice:
        message = await ctx.send("You need to be in a voice channel to use this command.")
        await message.delete(delay=ctx.bot.cleartimer)
        return
    
    voice_channel = ctx.author.voice.channel
    
    # If no query is provided, show the control panel
    if not query:
        await ctx.bot.join_and_show_controls(ctx.channel, voice_channel, ctx.guild.id)
        return
    
    # Check if the query is a URL
    is_url = query.startswith("http") and ("youtube.com" in query or "youtu.be" in query)
    
    if is_url:
        # Process URL directly
        try:
            # Normalize the URL
            url = ctx.bot.youtube_client.normalize_playlist_url(query)
            
            # Join voice channel and show controls first
            await ctx.bot.join_and_show_controls(ctx.channel, voice_channel, ctx.guild.id)
            
            # Process the URL
            result = await ctx.bot.youtube_client.process_youtube_url(url)
            
            if not result:
                message = await ctx.send("Could not process the URL. Please check the link and try again.")
                await message.delete(delay=ctx.bot.cleartimer)
                return
            
            # Handle different URL types
            if result['type'] == 'video':
                # Single video
                video_info = result['info']
                
                # Add to queue
                await add_to_queue(
                    ctx.bot,
                    str(ctx.guild.id), 
                    str(voice_channel.id), 
                    video_info['id'], 
                    video_info['title']
                )
                
            elif result['type'] == 'playlist':
                # Display loading message
                loading_msg = await ctx.send(f"Loading playlist: **{result['info'].get('title', 'Unknown')}**...")
                
                # Process playlist - add all tracks
                entries = result['entries']
                
                # Set flag for processing
                queue_id = ctx.bot.get_queue_id(str(ctx.guild.id), str(voice_channel.id))
                ctx.bot.playlist_processing[queue_id] = False
                
                # Add tracks
                added_count = 0
                failed_count = 0
                
                for entry in entries:
                    # Check if processing has been interrupted
                    if ctx.bot.playlist_processing.get(queue_id, False):
                        break
                    
                    try:
                        result = await add_to_queue(
                            ctx.bot,
                            str(ctx.guild.id), 
                            str(voice_channel.id), 
                            entry['id'], 
                            entry['title']
                        )
                        
                        if result["success"]:
                            added_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        print(f"Error adding track {entry['title']}: {e}")
                        failed_count += 1
                
                # Clean up processing flag
                ctx.bot.playlist_processing.pop(queue_id, None)
                
                # Delete loading message
                await loading_msg.delete()
                
                # Send summary
                summary_msg = await ctx.send(
                    f"Added **{added_count}** tracks from playlist to queue. Failed: **{failed_count}**"
                )
                await summary_msg.delete(delay=ctx.bot.cleartimer)
                
        except Exception as e:
            error_msg = await ctx.send(f"Error processing URL: {str(e)}")
            await error_msg.delete(delay=ctx.bot.cleartimer)
            
    else:
        # Treat as a search query
        try:
            # Join voice channel and show controls first
            await ctx.bot.join_and_show_controls(ctx.channel, voice_channel, ctx.guild.id)
            
            # Send searching message
            search_msg = await ctx.send(f"🔍 Searching for: **{query}**")
            
            # Search for videos
            search_results = await ctx.bot.youtube_client.search_videos(query)
            
            if not search_results:
                await search_msg.edit(content=f"❌ No results found for: **{query}**")
                await search_msg.delete(delay=ctx.bot.cleartimer)
                return
            
            # Get the first result
            video = search_results[0]
            
            # Add to queue
            result = await add_to_queue(
                ctx.bot,
                str(ctx.guild.id), 
                str(voice_channel.id), 
                video['id'], 
                video['title']
            )
            
            if result["success"]:
                # Edit the message to show the result
                await search_msg.edit(content=f"✅ Added to queue: **{video['title']}**")
                await search_msg.delete(delay=ctx.bot.cleartimer)
            else:
                await search_msg.edit(content=f"❌ Failed to add track: {result['message']}")
                await search_msg.delete(delay=ctx.bot.cleartimer)
                
        except Exception as e:
            error_msg = await ctx.send(f"Error searching for videos: {str(e)}")
            await error_msg.delete(delay=ctx.bot.cleartimer)




# Core play_next functionality - manages actual playback
async def play_next(bot, guild_id, channel_id):
    """
    Play the next song in the queue
    
    Args:
        bot: The Discord bot instance
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
    """
    queue_id = bot.get_queue_id(guild_id, channel_id)
    print(f"play_next called for queue {queue_id}")
    
    # Check if there are songs in the queue
    if not bot.music_queues[queue_id]:
        bot.currently_playing.pop(queue_id, None)
        print(f"No songs in queue {queue_id}, stopping playback")
        
        # Update control panels to show empty queue
        await bot.update_control_panel(guild_id, channel_id)
        return
    
    # Get guild and voice client
    voice_client, queue_id = await bot.get_voice_client(guild_id, channel_id, connect=True)
    if not voice_client:
        print(f"Could not connect to voice channel {channel_id} in guild {guild_id}")
        return
    
    # Get next song
    song = bot.music_queues[queue_id].pop(0)
    bot.currently_playing[queue_id] = song
    
    try:
        # Use the music client to get the audio URL
        audio_url = await bot.youtube_client.extract_audio_url(song['id'])
        
        if not audio_url:
            raise Exception(f"Failed to extract audio URL for {song['id']}")
        
        # Get FFmpeg options from the service
        ffmpeg_options = bot.youtube_client.get_ffmpeg_options('medium')
        
        # Create FFmpeg audio source
        audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        
        # Play the song
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next(bot, guild_id, channel_id), bot.loop) if e is None else print(f'Player error: {e}'))
        
        # Set the volume to a reasonable level
        voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=0.5)
        print(f"Now playing: {song['title']} in guild {guild_id}")
        
        # Update control panels with now playing information
        await bot.update_control_panel(guild_id, channel_id)
        
    except Exception as e:
        print(f"Error playing song: {e}")
        # Try to play the next song
        bot.currently_playing.pop(queue_id, None)
        asyncio.create_task(play_next(bot, guild_id, channel_id))