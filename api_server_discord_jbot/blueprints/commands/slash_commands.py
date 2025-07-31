"""
Smart slash commands for Discord bot - Single /jai command with context-aware behavior
"""
import discord
from discord.ext import commands
import asyncio

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"SlashCommands cog initialized with bot: {bot.user}")

    @discord.app_commands.command(name="jai", description="Smart music bot control - join/leave/play based on context")
    @discord.app_commands.describe(query="Optional: Song name, artist, or YouTube URL to play (leave empty to join/leave)")
    async def jai_slash(self, interaction: discord.Interaction, query: str = None):
        """
        Smart JAI command that behaves based on context:
        - If not joined + no query: Join voice channel and show controls
        - If not joined + has query: Join voice channel and play query
        - If joined + no query: Leave voice channel
        - If joined + has query: Play the query
        """
        print(f"JAI slash command called by {interaction.user} with query: {query}")
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
        
        try:
            # Check if bot is currently connected to a voice channel in this guild
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            is_connected = voice_client and voice_client.is_connected()
            
            # Determine action based on connection status and query
            if not is_connected:
                # Bot is not connected
                if query is None:
                    # Join and show controls
                    await self._join_and_show_controls(interaction, user_voice_channel)
                else:
                    # Join and play query
                    await self._join_and_play(interaction, user_voice_channel, query)
            else:
                # Bot is already connected
                if query is None:
                    # Leave voice channel
                    await self._leave_voice_channel(interaction, voice_client)
                else:
                    # Play query (check if user is in same channel first)
                    if interaction.user.voice.channel != voice_client.channel:
                        await interaction.followup.send(
                            f"❌ I'm already connected to **{voice_client.channel.name}**. "
                            f"Join that channel or use `/jai` without a query to make me leave first.",
                            ephemeral=True
                        )
                        return
                    
                    await self._play_query(interaction, user_voice_channel, query)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )

    async def _join_and_show_controls(self, interaction, voice_channel):
        """Join voice channel and show controls in jai text channel"""
        # Find or create jai channel
        jai_channel = await self._get_or_create_jai_channel(interaction.guild)
        if not jai_channel:
            await interaction.followup.send(
                "❌ Could not access or create the 'jai' text channel. Check bot permissions.",
                ephemeral=True
            )
            return
        
        # Join voice channel and show controls
        await self.bot.join_and_show_controls(jai_channel, voice_channel, interaction.guild.id)
        
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
        await self._countdown_and_cleanup(message, 8)

    async def _join_and_play(self, interaction, voice_channel, query):
        """Join voice channel and immediately play the query"""
        # Find or create jai channel
        jai_channel = await self._get_or_create_jai_channel(interaction.guild)
        if not jai_channel:
            await interaction.followup.send(
                "❌ Could not access or create the 'jai' text channel. Check bot permissions.",
                ephemeral=True
            )
            return
        
        # Join voice channel and show controls
        await self.bot.join_and_show_controls(jai_channel, voice_channel, interaction.guild.id)
        
        # Now play the query
        success_message = await self._process_and_play_query(interaction, voice_channel, query)
        
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
        await self._countdown_and_cleanup(message, 8)

    async def _leave_voice_channel(self, interaction, voice_client):
        """Leave the voice channel"""
        # Check if user is in the same voice channel
        if not interaction.user.voice or interaction.user.voice.channel != voice_client.channel:
            await interaction.followup.send(
                "❌ You need to be in the same voice channel to make me leave.",
                ephemeral=True
            )
            return
        
        channel_id = str(voice_client.channel.id)
        voice_channel_name = voice_client.channel.name
        
        # Disconnect from voice channel
        from .leave import disconnect_from_voice
        result = await disconnect_from_voice(self.bot, str(interaction.guild.id), channel_id, preserve_queue=False)
        
        await interaction.followup.send(
            f"{interaction.user.mention} ✅ Left **{voice_channel_name}** and cleared the queue.",
            ephemeral=True
        )

    async def _play_query(self, interaction, voice_channel, query):
        """Play a query in the already connected voice channel"""
        success_message = await self._process_and_play_query(interaction, voice_channel, query)
        
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

    async def _process_and_play_query(self, interaction, voice_channel, query):
        """Process and play a query, return success message or None if failed"""
        try:
            # Check if the query is a URL
            is_url = query.startswith("http") and ("youtube.com" in query or "youtu.be" in query)
            
            if is_url:
                # Process URL directly
                try:
                    # Normalize the URL
                    url = self.bot.youtube_client.normalize_playlist_url(query)
                    
                    # Process the URL
                    result = await self.bot.youtube_client.process_youtube_url(url)
                    
                    if not result:
                        return None
                    
                    # Handle different URL types
                    if result['type'] == 'video':
                        # Single video
                        video_info = result['info']
                        
                        # Add to queue
                        from .search import add_to_queue
                        queue_result = await add_to_queue(
                            self.bot,
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
                                    self.bot,
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
                    search_results = await self.bot.youtube_client.search_videos(query)
                    
                    if not search_results:
                        return None
                    
                    # Get the first result
                    video = search_results[0]
                    
                    # Add to queue
                    from .search import add_to_queue
                    result = await add_to_queue(
                        self.bot,
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
            print(f"Error in _process_and_play_query: {e}")
            return None

    async def _countdown_and_cleanup(self, message, seconds):
        """Show countdown and then delete the message"""
        try:
            # Get the original content
            original_content = message.content
            original_view = message.view
            
            # Countdown
            for remaining in range(seconds, 0, -1):
                await asyncio.sleep(1)
                try:
                    # Update message with countdown
                    countdown_content = f"{original_content}\n\n*This message will disappear in {remaining} second{'s' if remaining != 1 else ''}...*"
                    await message.edit(content=countdown_content, view=original_view)
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
                # Can't delete the message (maybe no permissions), just disable the view
                try:
                    await message.edit(view=None)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in countdown_and_cleanup: {e}")

    async def _get_or_create_jai_channel(self, guild):
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
                description="This channel has been created for music controls.\n\nUse `/jai` to get started!",
                color=discord.Color.green()
            )
            await jai_channel.send(embed=welcome_embed)
            
            return jai_channel
            
        except discord.Forbidden:
            return None
        except Exception as e:
            print(f"Error creating jai channel: {e}")
            return None

# Function to add the cog to the bot
async def setup(bot):
    print(f"Setting up SlashCommands cog for bot: {bot.user}")
    cog = SlashCommands(bot)
    await bot.add_cog(cog)
    print("SlashCommands cog added successfully")

# For registering with the bot
def apply_slash_commands(bot):
    """Apply slash commands to the bot"""
    print("Applying slash commands to bot")
    # Store the setup function to be called later when the event loop is running
    bot._slash_commands_setup = setup
    print("Slash commands setup function stored")