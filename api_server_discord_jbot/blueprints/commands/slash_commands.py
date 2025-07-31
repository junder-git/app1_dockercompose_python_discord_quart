"""
Smart slash commands for Discord bot - Single /jai command with action parameter
"""
import discord
import asyncio

# For registering with the bot
def apply_slash_commands(bot):
    """Apply slash commands to the bot"""
    print("Applying slash commands to bot - single command with action parameter")
    
    # Single JAI command with action parameter
    @discord.app_commands.command(name="jai", description="Music bot control - join, leave, or play music")
    @discord.app_commands.describe(action="Type 'join' to join voice, 'leave' to leave, or enter a song/URL to play")
    async def jai_command(interaction: discord.Interaction, action: str):
        """JAI command with action parameter"""
        print(f"JAI command called by {interaction.user} with action: {action}")
        
        # Check if user is in a voice channel (required for all operations)
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ You need to be in a voice channel to use JAI.", 
                ephemeral=True
            )
            return
        
        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        user_voice_channel = interaction.user.voice.channel
        action_lower = action.lower().strip()
        
        try:
            # Check if bot is currently connected to a voice channel in this guild
            voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
            is_connected = voice_client and voice_client.is_connected()
            
            if action_lower == "join":
                # JOIN ACTION
                if is_connected:
                    await interaction.followup.send(
                        f"❌ I'm already connected to **{voice_client.channel.name}**. Use `/jai leave` first.",
                        ephemeral=True
                    )
                    return
                
                await join_and_show_controls(bot, interaction, user_voice_channel)
                
            elif action_lower == "leave":
                # LEAVE ACTION
                if not is_connected:
                    await interaction.followup.send(
                        "❌ I'm not currently connected to any voice channel.",
                        ephemeral=True
                    )
                    return
                
                # Check if user is in the same voice channel
                if interaction.user.voice.channel != voice_client.channel:
                    await interaction.followup.send(
                        f"❌ I'm connected to **{voice_client.channel.name}**. Join that channel to make me leave.",
                        ephemeral=True
                    )
                    return
                
                await leave_voice_channel(bot, interaction, voice_client)
                
            else:
                # QUERY ACTION (anything that's not "join" or "leave")
                query = action  # The action IS the query
                
                if not is_connected:
                    # Join and play
                    await join_and_play(bot, interaction, user_voice_channel, query)
                else:
                    # Just play (if user is in same channel)
                    if interaction.user.voice.channel != voice_client.channel:
                        await interaction.followup.send(
                            f"❌ I'm connected to **{voice_client.channel.name}**. Join that channel to add songs.",
                            ephemeral=True
                        )
                        return
                    
                    await play_query(bot, interaction, user_voice_channel, query)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # Add the command to the tree
    bot.tree.add_command(jai_command)
    print("JAI command added to tree successfully")

async def join_and_show_controls(bot, interaction, voice_channel):
    """Join voice channel and show controls in jai text channel"""
    # Find or create jai channel
    jai_channel = await get_or_create_jai_channel(interaction.guild)
    if not jai_channel:
        await interaction.followup.send(
            "❌ Could not access or create the 'jai' text channel. Check bot permissions.",
            ephemeral=True
        )
        return
    
    # Join voice channel and show controls
    await bot.join_and_show_controls(jai_channel, voice_channel, interaction.guild.id)
    
    # Create a view with a button to navigate to the jai channel
    view = discord.ui.View(timeout=8)
    nav_button = discord.ui.Button(
        label="Go to JAI Channel",
        style=discord.ButtonStyle.primary,
        emoji="🎵",
        url=f"https://discord.com/channels/{interaction.guild.id}/{jai_channel.id}"
    )
    view.add_item(nav_button)
    
    # Send initial message
    message = await interaction.followup.send(
        f"{interaction.user.mention} ✅ Joined **{voice_channel.name}** and posted controls in {jai_channel.mention}!\n"
        f"Click the button below to go directly to the music controls:",
        view=view,
        ephemeral=True
    )
    
    # Start countdown and cleanup
    await countdown_and_cleanup(message, 8)

async def join_and_play(bot, interaction, voice_channel, query):
    """Join voice channel and immediately play the query"""
    # Find or create jai channel
    jai_channel = await get_or_create_jai_channel(interaction.guild)
    if not jai_channel:
        await interaction.followup.send(
            "❌ Could not access or create the 'jai' text channel. Check bot permissions.",
            ephemeral=True
        )
        return
    
    # Join voice channel and show controls
    await bot.join_and_show_controls(jai_channel, voice_channel, interaction.guild.id)
    
    # Now play the query
    success_message = await process_and_play_query(bot, interaction, voice_channel, query)
    
    # Create a view with a button to navigate to the jai channel
    view = discord.ui.View(timeout=8)
    nav_button = discord.ui.Button(
        label="Go to JAI Channel",
        style=discord.ButtonStyle.primary,
        emoji="🎵",
        url=f"https://discord.com/channels/{interaction.guild.id}/{jai_channel.id}"
    )
    view.add_item(nav_button)
    
    if success_message:
        message = await interaction.followup.send(
            f"{interaction.user.mention} ✅ Joined **{voice_channel.name}** and {success_message}\n"
            f"Click the button below to access music controls:",
            view=view,
            ephemeral=True
        )
    else:
        message = await interaction.followup.send(
            f"{interaction.user.mention} ✅ Joined **{voice_channel.name}** but failed to play the requested content.\n"
            f"Click the button below to access music controls:",
            view=view,
            ephemeral=True
        )
    
    # Start countdown and cleanup
    await countdown_and_cleanup(message, 8)

async def leave_voice_channel(bot, interaction, voice_client):
    """Leave the voice channel"""
    channel_id = str(voice_client.channel.id)
    voice_channel_name = voice_client.channel.name
    
    # Disconnect from voice channel
    from .leave import disconnect_from_voice
    result = await disconnect_from_voice(bot, str(interaction.guild.id), channel_id, preserve_queue=False)
    
    await interaction.followup.send(
        f"{interaction.user.mention} ✅ Left **{voice_channel_name}** and cleared the queue.",
        ephemeral=True
    )

async def play_query(bot, interaction, voice_channel, query):
    """Play a query in the already connected voice channel"""
    success_message = await process_and_play_query(bot, interaction, voice_channel, query)
    
    if success_message:
        await interaction.followup.send(
            f"{interaction.user.mention} ✅ {success_message}",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"{interaction.user.mention} ❌ Failed to play the requested content. Please check your query and try again.",
            ephemeral=True
        )

async def process_and_play_query(bot, interaction, voice_channel, query):
    """Process and play a query, return success message or None if failed"""
    try:
        # Check if the query is a URL
        is_url = query.startswith("http") and ("youtube.com" in query or "youtu.be" in query)
        
        if is_url:
            # Process URL directly
            try:
                # Normalize the URL
                url = bot.youtube_client.normalize_playlist_url(query)
                
                # Process the URL
                result = await bot.youtube_client.process_youtube_url(url)
                
                if not result:
                    return None
                
                # Handle different URL types
                if result['type'] == 'video':
                    # Single video
                    video_info = result['info']
                    
                    # Add to queue
                    from .search import add_to_queue
                    queue_result = await add_to_queue(
                        bot,
                        str(interaction.guild.id), 
                        str(voice_channel.id), 
                        video_info['id'], 
                        video_info['title']
                    )
                    
                    if queue_result["success"]:
                        return f"added to queue: **{video_info['title']}**"
                    else:
                        return None
                        
                elif result['type'] == 'playlist':
                    # Playlist - add first 10 tracks for slash command
                    entries = result['entries'][:10]  # Limit to first 10 for slash command
                    
                    added_count = 0
                    for entry in entries:
                        try:
                            from .search import add_to_queue
                            queue_result = await add_to_queue(
                                bot,
                                str(interaction.guild.id), 
                                str(voice_channel.id), 
                                entry['id'], 
                                entry['title']
                            )
                            
                            if queue_result["success"]:
                                added_count += 1
                        except Exception as e:
                            print(f"Error adding track {entry['title']}: {e}")
                    
                    if added_count > 0:
                        return f"added **{added_count}** tracks from playlist to queue"
                    else:
                        return None
                    
            except Exception as e:
                print(f"Error processing URL: {e}")
                return None
                
        else:
            # Treat as a search query
            try:
                # Search for videos
                search_results = await bot.youtube_client.search_videos(query)
                
                if not search_results:
                    return None
                
                # Get the first result
                video = search_results[0]
                
                # Add to queue
                from .search import add_to_queue
                result = await add_to_queue(
                    bot,
                    str(interaction.guild.id), 
                    str(voice_channel.id), 
                    video['id'], 
                    video['title']
                )
                
                if result["success"]:
                    return f"found and added: **{video['title']}**"
                else:
                    return None
                    
            except Exception as e:
                print(f"Error searching for videos: {e}")
                return None
        
    except Exception as e:
        print(f"Error in process_and_play_query: {e}")
        return None

async def countdown_and_cleanup(message, seconds):
    """Show countdown and then delete the message - fixed for webhook messages"""
    try:
        # Get the original content and view (handle webhook messages)
        original_content = message.content
        original_view = getattr(message, 'view', None)
        
        # Countdown
        for remaining in range(seconds, 0, -1):
            await asyncio.sleep(1)
            try:
                # Update message with countdown
                countdown_content = f"{original_content}\n\n*This message will disappear in {remaining} second{'s' if remaining != 1 else ''}...*"
                if original_view:
                    await message.edit(content=countdown_content, view=original_view)
                else:
                    await message.edit(content=countdown_content)
            except discord.NotFound:
                # Message was already deleted
                return
            except discord.HTTPException:
                # Error editing message, continue countdown
                continue
        
        # Delete the message
        try:
            await message.delete()
        except discord.NotFound:
            # Message was already deleted
            pass
        except discord.HTTPException:
            # Can't delete the message, try to disable view
            try:
                if original_view:
                    await message.edit(view=None)
            except:
                pass
                
    except Exception as e:
        print(f"Error in countdown_and_cleanup: {e}")

async def get_or_create_jai_channel(guild):
    """Find or create the jai text channel"""
    # First, try to find existing "jai" channel
    for channel in guild.text_channels:
        if channel.name.lower() == "jai":
            return channel
    
    # If no "jai" channel exists, create one
    try:
        jai_channel = await guild.create_text_channel(
            name="jai",
            topic="🎵 JAI Music Bot Control Panel",
            reason="Created by JAI music bot"
        )
        
        # Send welcome message to new channel
        welcome_embed = discord.Embed(
            title="🎵 Welcome to JAI Music Bot!",
            description="This channel has been created for music controls.\n\nUse `/jai join` to get started!",
            color=discord.Color.green()
        )
        await jai_channel.send(embed=welcome_embed)
        
        return jai_channel
        
    except discord.Forbidden:
        return None
    except Exception as e:
        print(f"Error creating jai channel: {e}")
        return None