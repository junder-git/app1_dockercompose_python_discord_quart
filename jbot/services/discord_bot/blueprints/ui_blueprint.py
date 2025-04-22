"""
Ui Blueprint for Discord Bot
Handles ui channel connections
"""
import types
import discord
import os
from clients.music_player import MusicPlayerClient
from clients.youtube_api import YouTubeClient

# Get API key for services (used by modals)
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared services (used by modals)
youtube_service = YouTubeClient(api_key=YOUTUBE_API_KEY)
music_service = MusicPlayerClient(api_key=YOUTUBE_API_KEY)

def apply(bot):
    """
    Apply ui blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind ui methods to the bot
    bot.join_and_show_controls = types.MethodType(join_and_show_controls, bot)
    bot.update_control_panel = types.MethodType(update_control_panel, bot)
    bot.send_control_panel = types.MethodType(send_control_panel, bot)

# UI Components for Discord Buttons
async def show_playlist_help(interaction: discord.Interaction):
    """Show help information about playlist selection options"""
    embed = discord.Embed(
        title="Playlist Selection Options",
        description="When adding a playlist, you can specify which tracks to add:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Leave Empty",
        value="Add all tracks from the playlist",
        inline=False
    )
    
    embed.add_field(
        name="Single Number",
        value="Add only the track at that position (e.g., `5` for the 5th track)",
        inline=False
    )
    
    embed.add_field(
        name="Range",
        value="Add tracks in that range (e.g., `5-10` for tracks 5 through 10)",
        inline=False
    )
    
    embed.add_field(
        name="Comma-separated Numbers",
        value="Add specific tracks (e.g., `1,3,5,9` for tracks 1, 3, 5, and 9)",
        inline=False
    )
    
    # Add a help button to the URL modal
    view = discord.ui.View(timeout=60)
    
    # Add a link button to dismiss
    dismiss_button = discord.ui.Button(
        label="Dismiss",
        style=discord.ButtonStyle.secondary,
        custom_id="dismiss_help"
    )
    async def dismiss_callback(interaction):
        await interaction.response.defer()
        await interaction.delete_original_message()
    
    dismiss_button.callback = dismiss_callback
    view.add_item(dismiss_button)
    
    # Send the help message
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True, delete_after=10)

class EnhancedURLModal(discord.ui.Modal):
    def __init__(self, bot, guild_id, channel_id):
        super().__init__(title="Add Song/Playlist URL")
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        
        # Add text input for URL
        self.url_input = discord.ui.TextInput(
            label="Enter YouTube URL",
            placeholder="Paste YouTube video or playlist URL",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.url_input)
        
        # Add optional text input for playlist selection
        self.playlist_options = discord.ui.TextInput(
            label="Playlist Options (Optional)",
            placeholder="Leave empty for all, or enter: index, range (x-y), or comma-separated indices",
            required=False,
            style=discord.TextStyle.short
        )
        self.add_item(self.playlist_options)

    def truncate_title(self, title, max_length=90):
        """Truncate title while preserving meaning"""
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."

    def parse_playlist_selection(self, selection_text, playlist_length):
        """Parse the playlist selection text and return selected indices"""
        if not selection_text or selection_text.strip() == "":
            # Return all indices if no selection is specified
            return list(range(playlist_length))
        
        selected_indices = []
        selection_text = selection_text.strip()
        
        try:
            # Case 1: Single index
            if selection_text.isdigit():
                index = int(selection_text)
                # Convert to 0-based index and validate
                index = index - 1 if index > 0 else index
                if 0 <= index < playlist_length:
                    selected_indices.append(index)
            
            # Case 2: Range (e.g., "5-10")
            elif "-" in selection_text and selection_text.count("-") == 1:
                start, end = selection_text.split("-")
                start = int(start.strip())
                end = int(end.strip())
                # Convert to 0-based indices
                start = start - 1 if start > 0 else start
                end = end - 1 if end > 0 else end
                # Validate and add range
                if 0 <= start <= end < playlist_length:
                    selected_indices.extend(range(start, end + 1))
            
            # Case 3: Comma-separated indices (e.g., "1,3,5")
            elif "," in selection_text:
                indices = [int(idx.strip()) for idx in selection_text.split(",")]
                # Convert to 0-based indices and validate
                indices = [idx - 1 if idx > 0 else idx for idx in indices]
                selected_indices.extend([idx for idx in indices if 0 <= idx < playlist_length])
            
            # If nothing was added or parsing failed, return all indices
            if not selected_indices:
                selected_indices = list(range(playlist_length))
        
        except ValueError:
            # If parsing fails, return all indices
            selected_indices = list(range(playlist_length))
        
        return selected_indices

    async def on_submit(self, modal_interaction: discord.Interaction):
        # Defer the interaction to give time for processing
        await modal_interaction.response.defer(ephemeral=True)
        
        # Verify and normalize the URL
        url = self.url_input.value.strip()
        url = youtube_service.normalize_playlist_url(url)
        
        try:
            # Check if user is in the same voice channel
            if not await self.bot.check_same_voice_channel(modal_interaction.user, self.channel_id):
                message = await modal_interaction.followup.send("You need to be in the same voice channel to add tracks.", ephemeral=True)
                await message.delete(delay=10)
                return
            
            # Process the URL using the shared MusicService
            result = await music_service.process_youtube_url(url)
            
            if not result:
                message = await modal_interaction.followup.send(
                    "Could not process the URL. Please check the link and try again.", 
                    ephemeral=True
                )
                await message.delete(delay=10)
                return
            
            # Handle different URL types
            if result['type'] == 'video':
                # Single video
                video_info = result['info']
                
                # Add to queue
                queue_result = await self.bot.add_to_queue(
                    self.guild_id, 
                    self.channel_id, 
                    video_info['id'], 
                    video_info['title']
                )
                
                if queue_result['success']:
                    message = await modal_interaction.followup.send(
                        f"Added to queue: **{video_info['title']}**", 
                        ephemeral=True
                    )
                    await message.delete(delay=10)
                else:
                    message = await modal_interaction.followup.send(
                        "Failed to add track to queue.", 
                        ephemeral=True
                        )
                    await message.delete(delay=10)
            
            elif result['type'] == 'playlist':
                # Playlist
                playlist_info = result['info']
                entries = result['entries']
                
                # Parse playlist selection options
                selected_indices = self.parse_playlist_selection(
                    self.playlist_options.value, 
                    len(entries)
                )
                
                # Display a summary of what will be added
                selection_summary = ""
                if len(selected_indices) == 1:
                    index = selected_indices[0]
                    selection_summary = f"Adding track #{index+1} from playlist"
                elif len(selected_indices) == len(entries):
                    selection_summary = f"Adding all {len(entries)} tracks from playlist"
                elif len(selected_indices) < 10:
                    indices_str = ", ".join(str(i+1) for i in selected_indices)
                    selection_summary = f"Adding tracks {indices_str} from playlist"
                else:
                    selection_summary = f"Adding {len(selected_indices)} tracks from playlist"
                
                message = await modal_interaction.followup.send(
                    f"Processing: **{playlist_info.get('title', 'Unnamed Playlist')}**\n{selection_summary}...", 
                    ephemeral=True
                )
                await message.delete(delay=10)
                
                # Set flag to indicate processing has started
                queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
                self.bot.playlist_processing[queue_id] = False
                
                # Add selected tracks to queue
                added_count = 0
                failed_count = 0
                interrupted = False
                
                for idx in selected_indices:
                    # Check if processing has been interrupted
                    if self.bot.playlist_processing.get(queue_id, False):
                        interrupted = True
                        break
                    
                    if 0 <= idx < len(entries):
                        entry = entries[idx]
                        try:
                            queue_result = await self.bot.add_to_queue(
                                self.guild_id, 
                                self.channel_id, 
                                entry['id'], 
                                entry['title']
                            )
                            
                            if queue_result['success']:
                                added_count += 1
                            else:
                                failed_count += 1
                        except Exception as e:
                            print(f"Error adding track {entry['title']}: {e}")
                            failed_count += 1
                
                # Clean up processing flag
                self.bot.playlist_processing.pop(queue_id, None)
                
                # Send summary message
                message = f"Playlist **{playlist_info.get('title', 'Unnamed Playlist')}**:\n"
                message += f"✅ Added {added_count} tracks\n"
                
                if interrupted:
                    message += f"⏹️ Playlist addition interrupted\n"
                
                message += f"❌ Failed to add {failed_count} tracks"
                
                messagetemp = await modal_interaction.followup.send(message, ephemeral=True)
                await messagetemp.delete(delay=10)
        
        except Exception as e:
            print(f"Error adding URL: {e}")
            message = await modal_interaction.followup.send(
                f"Error adding URL: {str(e)}", 
                ephemeral=True
            )
            await message.delete(delay=10)

class SearchModal(discord.ui.Modal):
    def __init__(self, bot, guild_id, channel_id):
        super().__init__(title="Search for a Song")
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        
        # Add text input for search query
        self.query = discord.ui.TextInput(
            label="Enter song name or keywords",
            placeholder="e.g. Coldplay Yellow",
            required=True,
            max_length=100
        )
        self.add_item(self.query)
    
    async def on_submit(self, modal_interaction: discord.Interaction):
        # Defer the interaction to give time for processing
        await modal_interaction.response.defer(ephemeral=True)
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(modal_interaction.user, self.channel_id):
            message = await modal_interaction.followup.send("You need to be in the same voice channel to search.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared MusicService for search
        try:
            # Use optimized search instead of direct yt-dlp
            results = await music_service.search_videos(self.query.value)
            
            if not results:
                message = await modal_interaction.followup.send(f"No results found for: {self.query.value}", ephemeral=True)
                await message.delete(delay=10)
                return
            
            # Create embed for results
            embed = discord.Embed(
                title=f"Search Results for: {self.query.value}",
                description="Select a track to play",
                color=discord.Color.green()
            )
            
            # Create dropdown menu for selecting tracks
            select = discord.ui.Select(
                placeholder="Choose a track",
                min_values=1,
                max_values=1,
                custom_id="search_results"
            )
            
            # Add options to select menu
            for i, result in enumerate(results):
                # Truncate title to fit Discord's label requirements
                def truncate_title(title, max_length=90):
                    """Truncate title while preserving meaning"""
                    if len(title) <= max_length:
                        return title
                    return title[:max_length-3] + "..."
                
                # Sanitize title for label
                safe_title = truncate_title(result['title'])
                
                # Get duration
                duration = result.get('duration')
                if duration:
                    minutes, seconds = divmod(duration, 60)
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"
                
                # Add to embed
                embed.add_field(
                    name=f"{i+1}. {safe_title}",
                    value=f"Duration: {duration_str}",
                    inline=False
                )
                
                # Add to select menu
                select.add_option(
                    label=f"{i+1}. {safe_title}",
                    value=f"{result['id']}",
                    description=f"Duration: {duration_str}"
                )
            
            # Create view and add select
            view = discord.ui.View(timeout=60)
            view.add_item(select)
            
            # Define select callback
            async def select_callback(interaction):
                # Ensure the user who submitted the modal is making the selection
                if interaction.user != modal_interaction.user:
                    await interaction.response.send_message(
                        "Only the person who used the search command can select a track.",
                        ephemeral=True
                    )
                    return
                
                # Get the selected track ID
                video_id = interaction.data['values'][0]
                
                # Find the selected track in the results
                selected_track = None
                for result in results:
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
                
                # Use the shared add_to_queue method
                result = await self.bot.add_to_queue(
                    self.guild_id, 
                    self.channel_id, 
                    selected_track['id'], 
                    selected_track['title']
                )
                
                # Confirm selection
                message = await interaction.followup.send(
                    f"Added to queue: **{selected_track['title']}**",
                    ephemeral=True
                )
                await message.delete(delay=10)
            
            # Assign callback
            select.callback = select_callback
            
            # Send results as a followup to the modal
            message = await modal_interaction.followup.send(embed=embed, view=view, ephemeral=True)
            await message.delete(delay=10)
                
        except Exception as e:
            print(f"Error searching for videos: {e}")
            message = await modal_interaction.followup.send(f"An error occurred while searching: {str(e)}", ephemeral=True)
            await message.delete(delay=10)
# UI Components for Discord Buttons
class MusicControlView(discord.ui.View):
    def __init__(self, bot, guild_id, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.queue_id = bot.get_queue_id(guild_id, channel_id)

        # Create a link button for web player
        web_player_button = discord.ui.Button(
            label="Web Player", 
            style=discord.ButtonStyle.link, 
            url="https://music.junder.uk",
            row=2
        )
        self.add_item(web_player_button)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.secondary, emoji="🔍", custom_id="search", row=2)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send the search modal
        await interaction.response.send_modal(SearchModal(self.bot, self.guild_id, self.channel_id))
    
    @discord.ui.button(label="Add URL", style=discord.ButtonStyle.secondary, emoji="🔗", custom_id="add_url", row=2)
    async def add_url_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send the enhanced URL modal
        await interaction.response.send_modal(EnhancedURLModal(self.bot, self.guild_id, self.channel_id))
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="playlist_help", row=2)
    async def playlist_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_playlist_help(interaction)
    
    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.primary, emoji="⏯️", custom_id="play_pause")
    async def play_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared toggle play/pause method
        result = await self.bot.toggle_playback(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared skip method
        result = await self.bot.skip_track(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared stop method
        result = await self.bot.stop_playback(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀", custom_id="shuffle", row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared shuffle method
        result = await self.bot.shuffle_queue(self.guild_id, self.channel_id)
        
        # Send response that will auto-delete after 10 seconds
        message = message = await interaction.followup.send(result["message"])
        await message.delete(delay=10)
        
        # Update the control panel to show the new queue order
        await self.bot.update_control_panel(self.guild_id, self.channel_id)

    @discord.ui.button(label="Follow VC", style=discord.ButtonStyle.secondary, emoji="👣", custom_id="follow_vc", row=1)
    async def follow_vc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in a voice channel, but not necessarily the same one
        if not interaction.user.voice:
            message = await interaction.followup.send("You need to be in a voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Get the user's current voice channel
        new_voice_channel = interaction.user.voice.channel
        
        # If user is already in the same voice channel as the bot, no need to move
        if str(new_voice_channel.id) == self.channel_id:
            message = await interaction.followup.send("I'm already in your voice channel!", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Call a new method to handle the follow VC functionality
        result = await self.bot.follow_to_voice_channel(
            self.guild_id,
            self.channel_id,  # Current voice channel
            str(new_voice_channel.id),  # New voice channel
            interaction.user
        )
        
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, emoji="👋", custom_id="disconnect", row=1)
    async def disconnect_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared disconnect method
        result = await self.bot.disconnect_from_voice(self.guild_id, self.channel_id, preserve_queue=True)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
        # Delete the control panel message
        try:
            channel = interaction.channel
            if channel.id in self.bot.control_panels:
                message_id = self.bot.control_panels[channel.id]
                message = await channel.fetch_message(message_id)
                await message.delete()
                # Remove from control panels dictionary
                self.bot.control_panels.pop(channel.id, None)
        except Exception as e:
            print(f"Error removing control panel: {e}")

async def join_and_show_controls(self, text_channel, voice_channel, guild_id):
    """
    Join a voice channel and show controls in the text channel
    
    Args:
        text_channel: Discord text channel to send controls to
        voice_channel: Discord voice channel to join
        guild_id: ID of the Discord guild
    """
    try:
        # Check if we're already in this voice channel
        queue_id = self.get_queue_id(str(guild_id), str(voice_channel.id))
        
        # If already connected to a different channel, disconnect first
        for existing_queue_id, voice_client in list(self.voice_connections.items()):
            if existing_queue_id.startswith(f"{guild_id}_") and voice_client.is_connected():
                # Preserve queue if we're moving channels
                if existing_queue_id != queue_id and queue_id in self.currently_playing:
                    current_track = self.currently_playing.get(queue_id)
                    if current_track:
                        self.music_queues[queue_id].insert(0, current_track)
                
                await voice_client.disconnect(force=True)
                self.voice_connections.pop(existing_queue_id, None)
                break
        
        # Join the voice channel if not already connected
        if queue_id not in self.voice_connections or not self.voice_connections[queue_id].is_connected():
            voice_client = await voice_channel.connect()
            self.voice_connections[queue_id] = voice_client
            
            # Get cleartimer or default to 10 seconds
            cleartimer = getattr(self, 'cleartimer', 10)
            await text_channel.send(f"Joined **{voice_channel.name}**", delete_after=cleartimer)
        
        # Create and send control panel
        await self.send_control_panel(text_channel, voice_channel, str(guild_id))
        
    except Exception as e:
        print(f"Error joining voice channel: {e}")
        # Get cleartimer or default to 10 seconds
        cleartimer = getattr(self, 'cleartimer', 10)
        await text_channel.send(f"Error: {str(e)}", delete_after=cleartimer)

async def send_control_panel(self, text_channel, voice_channel, guild_id):
    """
    Send a control panel with buttons to the text channel
    
    Args:
        text_channel: Discord text channel object
        voice_channel: Discord voice channel object
        guild_id: Discord guild ID
    """
    queue_id = self.get_queue_id(guild_id, str(voice_channel.id))
    
    # Create embed for the control panel
    embed = discord.Embed(
        title="🎵 Music Control Panel",
        description=f"Connected to **{voice_channel.name}**",
        color=discord.Color.blurple()
    )
    
    # Add queue info if there are songs
    if self.music_queues[queue_id]:
        queue_text = "\n".join(
            f"{i+1}. {track['title']}" 
            for i, track in enumerate(self.music_queues[queue_id][:5])
        )
        if len(self.music_queues[queue_id]) > 5:
            queue_text += f"\n... and {len(self.music_queues[queue_id]) - 5} more"
        embed.add_field(name="Queue", value=queue_text or "Empty", inline=False)
    else:
        embed.add_field(name="Queue", value="Empty", inline=False)
    
    # Add currently playing info
    current_track = self.currently_playing.get(queue_id)
    if current_track:
        embed.add_field(
            name="Now Playing",
            value=f"[{current_track['title']}](https://www.youtube.com/watch?v={current_track['id']})",
            inline=False
        )
    
    # Create view with buttons
    view = MusicControlView(self, guild_id, str(voice_channel.id))
    
    # Send or update the control panel
    if text_channel.id in self.control_panels:
        try:
            # Try to edit existing message
            existing_message = await text_channel.fetch_message(self.control_panels[text_channel.id])
            await existing_message.edit(embed=embed, view=view)
            return
        except (discord.NotFound, discord.HTTPException):
            # Message doesn't exist anymore, send a new one
            pass
    
    # Send new control panel
    message = await text_channel.send(embed=embed, view=view)
    self.control_panels[text_channel.id] = message.id

async def update_control_panel(self, guild_id, channel_id):
    """
    Update all control panels for a guild/channel
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
    """
    queue_id = self.get_queue_id(guild_id, channel_id)
    
    # Find text channels with control panels for this guild
    guild = self.get_guild(int(guild_id))
    if not guild:
        return
    
    # Update all control panels in this guild
    for text_channel_id, message_id in list(self.control_panels.items()):
        try:
            text_channel = guild.get_channel(text_channel_id)
            if not text_channel:
                continue
            
            voice_channel = guild.get_channel(int(channel_id))
            if not voice_channel:
                continue
            
            # Update the control panel
            await self.send_control_panel(text_channel, voice_channel, guild_id)
        except Exception as e:
            print(f"Error updating control panel: {e}")

