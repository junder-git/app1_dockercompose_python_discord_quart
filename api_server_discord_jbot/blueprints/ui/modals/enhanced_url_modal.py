"""
Enhanced URL Modal for adding songs and playlists - Single input with dynamic playlist selection
"""
import os
import discord
import re
import asyncio
from api_client_youtube.__main__ import ClientYouTube

# Get API key for services
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared YouTube client
youtube_service = ClientYouTube(api_key=YOUTUBE_API_KEY)

class PlaylistSelectionView(discord.ui.View):
    """View for playlist selection after detecting a playlist URL"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.playlist_info = playlist_info
        self.entries = entries
        
        # Add dropdown for quick selection
        self.add_quick_select_dropdown()
        
        # Add custom input for advanced selection
        self.add_item(CustomSelectionButton(bot, guild_id, channel_id, playlist_info, entries))
    
    def add_quick_select_dropdown(self):
        """Add dropdown for common playlist selection options"""
        select = discord.ui.Select(
            placeholder="Choose how many tracks to add",
            min_values=1,
            max_values=1,
            custom_id="playlist_quick_select"
        )
        
        playlist_length = len(self.entries)
        
        # Add common options
        options = [
            ("All tracks", "all", f"Add all {playlist_length} tracks"),
            ("First 10", "1-10", "Add first 10 tracks"),
            ("First 25", "1-25", "Add first 25 tracks"),
            ("First 50", "1-50", "Add first 50 tracks"),
        ]
        
        # Only add options that make sense for the playlist length
        for label, value, description in options:
            if value == "all" or "-" not in value:
                select.add_option(label=label, value=value, description=description)
            else:
                # Parse range to check if it's valid
                try:
                    start, end = map(int, value.split("-"))
                    if end <= playlist_length:
                        select.add_option(label=label, value=value, description=description)
                    elif start <= playlist_length:
                        # Adjust the range to fit
                        adjusted_label = f"First {playlist_length}"
                        adjusted_value = f"1-{playlist_length}"
                        adjusted_desc = f"Add first {playlist_length} tracks"
                        select.add_option(label=adjusted_label, value=adjusted_value, description=adjusted_desc)
                except:
                    continue
        
        # Add random selection option
        if playlist_length > 20:
            select.add_option(label="Random 20", value="random-20", description="Add 20 random tracks")
        
        async def select_callback(interaction):
            await interaction.response.defer()
            selection = interaction.data['values'][0]
            
            # Process the selection
            await self.process_playlist_with_selection(selection, interaction)
        
        select.callback = select_callback
        self.add_item(select)
    
    async def process_playlist_with_selection(self, selection, interaction):
        """Process playlist with the given selection"""
        try:
            # Parse selection
            if selection == "all":
                selected_indices = list(range(len(self.entries)))
            elif selection.startswith("random-"):
                import random
                count = int(selection.split("-")[1])
                selected_indices = random.sample(range(len(self.entries)), min(count, len(self.entries)))
                selected_indices.sort()
            elif "-" in selection:
                start, end = map(int, selection.split("-"))
                selected_indices = list(range(start - 1, min(end, len(self.entries))))
            else:
                # Fallback - treat as single number
                try:
                    index = int(selection) - 1
                    selected_indices = [index] if 0 <= index < len(self.entries) else []
                except:
                    selected_indices = list(range(len(self.entries)))
            
            # Limit to prevent abuse
            max_tracks = 100
            if len(selected_indices) > max_tracks:
                selected_indices = selected_indices[:max_tracks]
            
            # Create selection summary
            if len(selected_indices) == 1:
                selection_summary = f"track #{selected_indices[0]+1}"
            elif len(selected_indices) == len(self.entries):
                selection_summary = f"all {len(self.entries)} tracks"
            else:
                selection_summary = f"{len(selected_indices)} selected tracks"
            
            # Update the selection message to show processing
            playlist_title = self.playlist_info.get('title', 'Unnamed Playlist')[:90]
            
            embed = discord.Embed(
                title="🔄 Processing Playlist",
                description=f"**{playlist_title}**\nAdding {selection_summary}...",
                color=discord.Color.orange()
            )
            
            await interaction.edit_original_response(embed=embed, view=None)
            
            # Disable main control panel buttons during processing
            await self.disable_main_control_panel()
            
            # Process the playlist
            await self.add_tracks_to_queue(selected_indices, playlist_title, interaction)
            
        except Exception as e:
            print(f"Error processing playlist selection: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process playlist selection.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            
            # Restore main control panel after error
            await asyncio.sleep(3)
            await self.restore_main_control_panel()
            
            # Delete this selection message
            await asyncio.sleep(2)
            try:
                await interaction.delete_original_response()
            except:
                pass
    
    async def add_tracks_to_queue(self, selected_indices, playlist_title, interaction):
        """Add selected tracks to the queue"""
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = False
        
        added_count = 0
        failed_count = 0
        batch_size = 10
        total_selected = len(selected_indices)
        
        try:
            for i in range(0, len(selected_indices), batch_size):
                # Check if processing was interrupted
                if self.bot.playlist_processing.get(queue_id, False):
                    break
                
                batch_indices = selected_indices[i:i + batch_size]
                
                # Process batch
                for idx in batch_indices:
                    if self.bot.playlist_processing.get(queue_id, False):
                        break
                        
                    if 0 <= idx < len(self.entries):
                        entry = self.entries[idx]
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
                            print(f"Error adding track {entry.get('title', 'Unknown')}: {e}")
                            failed_count += 1
                
                # Update progress every batch
                progress = min(i + batch_size, total_selected)
                if progress < total_selected and not self.bot.playlist_processing.get(queue_id, False):
                    try:
                        embed = discord.Embed(
                            title="🔄 Processing Playlist",
                            description=f"**{playlist_title}**\nProgress: {progress}/{total_selected} tracks...",
                            color=discord.Color.orange()
                        )
                        await interaction.edit_original_response(embed=embed)
                    except:
                        pass
            
            # Clean up processing flag
            self.bot.playlist_processing.pop(queue_id, None)
            
            # Create final result embed
            embed = discord.Embed(
                title="✅ Playlist Processed" if added_count > 0 else "❌ Playlist Failed",
                color=discord.Color.green() if added_count > 0 else discord.Color.red()
            )
            
            result_text = f"**{playlist_title}**\n"
            if added_count > 0:
                result_text += f"✅ Added {added_count} tracks\n"
            if failed_count > 0:
                result_text += f"❌ Failed to add {failed_count} tracks\n"
            if self.bot.playlist_processing.get(queue_id, False):
                result_text += "⏹️ Process interrupted"
            
            embed.description = result_text
            await interaction.edit_original_response(embed=embed)
            
            # Wait a moment then clean up
            await asyncio.sleep(5)
            
            # Restore main control panel
            await self.restore_main_control_panel()
            
            # Delete this selection message
            try:
                await interaction.delete_original_response()
            except:
                pass
            
        except Exception as e:
            print(f"Error in add_tracks_to_queue: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while adding tracks to the queue.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)
            
            # Restore main control panel after error
            await asyncio.sleep(3)
            await self.restore_main_control_panel()
            
            # Delete this selection message
            await asyncio.sleep(2)
            try:
                await interaction.delete_original_response()
            except:
                pass
    
    async def disable_main_control_panel(self):
        """Disable the main control panel buttons by replacing with DJ-ing message"""
        try:
            # Get guild and voice channel
            guild = self.bot.get_guild(int(self.guild_id))
            voice_channel = guild.get_channel(int(self.channel_id))
            
            # Create DJ-ing embed
            embed = discord.Embed(
                title="🎧 DJ is Working...",
                description=f"Connected to **{voice_channel.name}**\n\n🎵 Adding tracks to your queue...\n\n*Please wait while I process your selection*",
                color=discord.Color.orange()
            )
            
            # Update all control panels with DJ-ing message and no buttons
            for text_channel_id, message_id in list(self.bot.control_panels.items()):
                try:
                    text_channel = guild.get_channel(text_channel_id)
                    if text_channel:
                        message = await text_channel.fetch_message(message_id)
                        await message.edit(embed=embed, view=None)
                except Exception as e:
                    print(f"Error updating control panel to DJ mode: {e}")
                    
        except Exception as e:
            print(f"Error disabling main control panel: {e}")
    
    async def restore_main_control_panel(self):
        """Restore the main control panel with all buttons"""
        try:
            # Update the control panel to show current state with buttons restored
            await self.bot.update_control_panel(self.guild_id, self.channel_id)
        except Exception as e:
            print(f"Error restoring main control panel: {e}")


class CustomSelectionButton(discord.ui.Button):
    """Button to open custom selection modal"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries):
        super().__init__(
            label="Custom Selection",
            style=discord.ButtonStyle.secondary,
            emoji="⚙️"
        )
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.playlist_info = playlist_info
        self.entries = entries
    
    async def callback(self, interaction):
        # Show custom selection modal
        custom_modal = CustomPlaylistSelectionModal(
            self.bot, self.guild_id, self.channel_id, 
            self.playlist_info, self.entries
        )
        await interaction.response.send_modal(custom_modal)


class CustomPlaylistSelectionModal(discord.ui.Modal):
    """Modal for custom playlist selection input"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries):
        super().__init__(title="Custom Playlist Selection")
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.playlist_info = playlist_info
        self.entries = entries
        
        self.selection_input = discord.ui.TextInput(
            label="Track Selection",
            placeholder="Examples: 5 | 1-10 | 1,3,5,7 | 10-15,20,25-30",
            required=True,
            style=discord.TextStyle.short,
            max_length=100
        )
        self.add_item(self.selection_input)
    
    def parse_selection(self, selection_text, playlist_length):
        """Parse custom selection text"""
        selected_indices = set()
        
        if not selection_text.strip():
            return list(range(playlist_length))
        
        try:
            parts = [part.strip() for part in selection_text.split(',') if part.strip()]
            
            for part in parts:
                if '-' in part and part.count('-') == 1:
                    # Range
                    start_str, end_str = part.split('-')
                    start = max(1, int(start_str.strip()))
                    end = max(1, int(end_str.strip()))
                    
                    if start > end:
                        start, end = end, start
                    
                    for i in range(start - 1, min(end, playlist_length)):
                        selected_indices.add(i)
                        
                elif part.isdigit():
                    # Single index
                    index = max(1, int(part)) - 1
                    if index < playlist_length:
                        selected_indices.add(index)
        
        except Exception as e:
            print(f"Error parsing selection: {e}")
            return list(range(playlist_length))
        
        result = sorted(list(selected_indices))
        return result if result else list(range(playlist_length))
    
    async def on_submit(self, interaction):
        await interaction.response.defer()
        
        try:
            selected_indices = self.parse_selection(self.selection_input.value, len(self.entries))
            
            # Limit selection
            max_tracks = 100
            if len(selected_indices) > max_tracks:
                selected_indices = selected_indices[:max_tracks]
            
            if not selected_indices:
                embed = discord.Embed(
                    title="❌ Invalid Selection",
                    description="No valid tracks selected. Please check your input format.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create selection summary
            if len(selected_indices) == 1:
                selection_summary = f"track #{selected_indices[0]+1}"
            elif len(selected_indices) == len(self.entries):
                selection_summary = f"all {len(self.entries)} tracks"
            else:
                selection_summary = f"{len(selected_indices)} selected tracks"
            
            # Show confirmation and start processing
            playlist_title = self.playlist_info.get('title', 'Unnamed Playlist')[:90]
            
            embed = discord.Embed(
                title="🔄 Processing Custom Selection",
                description=f"**{playlist_title}**\nAdding {selection_summary}...",
                color=discord.Color.orange()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Create a view to process the selection
            view = PlaylistSelectionView(
                self.bot, self.guild_id, self.channel_id,
                self.playlist_info, self.entries
            )
            
            # Disable main control panel during processing
            await view.disable_main_control_panel()
            
            # Process the tracks
            await view.add_tracks_to_queue(selected_indices, playlist_title, interaction)
            
        except Exception as e:
            print(f"Error in custom selection: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process custom selection.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Restore main control panel on error
            try:
                view = PlaylistSelectionView(
                    self.bot, self.guild_id, self.channel_id,
                    self.playlist_info, self.entries
                )
                await view.restore_main_control_panel()
            except:
                pass


class EnhancedURLModal(discord.ui.Modal):
    def __init__(self, bot, guild_id, channel_id):
        super().__init__(title="Add YouTube URL")
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        
        # Single input for any YouTube URL
        self.url_input = discord.ui.TextInput(
            label="YouTube URL",
            placeholder="Paste any YouTube video or playlist URL",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        self.add_item(self.url_input)

    def normalize_youtube_url(self, url):
        """Normalize various YouTube URL formats to standard format"""
        url = url.strip()
        url = re.sub(r'\s+', '', url)
        
        # Check if it's already a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return f'https://www.youtube.com/watch?v={url}'
        
        # Extract video ID from various URL formats
        video_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]{11})',
            r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'gaming\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        ]
        
        # Extract playlist ID from various URL formats
        playlist_patterns = [
            r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?.*?list=([a-zA-Z0-9_-]+)',
            r'youtu\.be/.*?\?.*?list=([a-zA-Z0-9_-]+)',
            r'm\.youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
            r'm\.youtube\.com/watch\?.*?list=([a-zA-Z0-9_-]+)',
        ]
        
        # Try to extract video ID
        for pattern in video_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                # Check if there's also a playlist ID
                for pl_pattern in playlist_patterns:
                    pl_match = re.search(pl_pattern, url, re.IGNORECASE)
                    if pl_match:
                        playlist_id = pl_match.group(1)
                        return f'https://www.youtube.com/watch?v={video_id}&list={playlist_id}'
                return f'https://www.youtube.com/watch?v={video_id}'
        
        # Try playlist only
        for pattern in playlist_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                playlist_id = match.group(1)
                return f'https://www.youtube.com/playlist?list={playlist_id}'
        
        # Return as-is if it contains youtube
        if 'youtube' in url.lower() or 'youtu.be' in url.lower():
            return url
        
        return None

    async def on_submit(self, interaction):  
        # Defer the modal response immediately
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check if user is in voice channel
            if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
                await interaction.followup.send(
                    "❌ You need to be in the same voice channel to add tracks.", 
                    ephemeral=True
                )
                return
            
            # Normalize URL
            url = self.normalize_youtube_url(self.url_input.value)
            if not url:
                await interaction.followup.send(
                    "❌ Invalid YouTube URL format. Please check the URL and try again.", 
                    ephemeral=True
                )
                return
            
            # Disable main control panel during processing
            await self.disable_main_control_panel("🔄 Analyzing URL...")
            
            # Process URL
            result = await youtube_service.process_youtube_url(url)
            
            if not result:
                await self.restore_main_control_panel()
                await interaction.followup.send(
                    "❌ Could not process the URL. The video/playlist might be private, deleted, or region-locked.", 
                    ephemeral=True
                )
                return
            
            if result['type'] == 'video':
                # Single video - add directly
                await self.handle_single_video(interaction, result)
                
            elif result['type'] == 'playlist':
                # Playlist - show selection interface
                await self.handle_playlist(interaction, result)
            
        except Exception as e:
            print(f"Error processing URL: {e}")
            await self.restore_main_control_panel()
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}", 
                ephemeral=True
            )

    async def handle_single_video(self, interaction, result):
        """Handle single video URL"""
        try:
            video_info = result['info']
            
            # Update main panel status
            await self.disable_main_control_panel(f"🔄 Adding: {video_info['title'][:50]}...")
            
            # Add to queue
            queue_result = await self.bot.add_to_queue(
                self.guild_id, 
                self.channel_id, 
                video_info['id'], 
                video_info['title']
            )
            
            if queue_result['success']:
                # Show success briefly
                await self.disable_main_control_panel(f"✅ Added: {video_info['title'][:50]}")
                await asyncio.sleep(3)
                
                # Restore control panel
                await self.restore_main_control_panel()
                
                # Send ephemeral confirmation
                await interaction.followup.send(
                    f"✅ **{video_info['title']}** added to queue!", 
                    ephemeral=True
                )
            else:
                await self.restore_main_control_panel()
                await interaction.followup.send(
                    f"❌ Could not add video: {queue_result.get('message', 'Unknown error')}", 
                    ephemeral=True
                )
            
        except Exception as e:
            print(f"Error handling single video: {e}")
            await self.restore_main_control_panel()
            await interaction.followup.send(
                "❌ Failed to process video.", 
                ephemeral=True
            )

    async def handle_playlist(self, interaction, result):
        """Handle playlist URL - show selection interface"""
        try:
            playlist_info = result['info']
            entries = result['entries']
            
            if not entries:
                await self.restore_main_control_panel()
                await interaction.followup.send(
                    "❌ The playlist is empty or could not be accessed.", 
                    ephemeral=True
                )
                return
            
            # Restore main control panel first
            await self.restore_main_control_panel()
            
            # Create playlist selection interface as a separate message
            playlist_title = playlist_info.get('title', 'Unnamed Playlist')
            
            embed = discord.Embed(
                title="🎵 Playlist Detected",
                description=f"**{playlist_title}**\n\n📊 Contains **{len(entries)}** tracks\n\nHow many tracks would you like to add?",
                color=discord.Color.blue()
            )
            
            # Show first few tracks as preview
            if entries:
                preview_tracks = []
                for i, entry in enumerate(entries[:5]):
                    title = entry.get('title', 'Unknown Title')
                    if len(title) > 50:
                        title = title[:47] + "..."
                    preview_tracks.append(f"{i+1}. {title}")
                
                embed.add_field(
                    name="Preview (First 5 tracks)",
                    value="\n".join(preview_tracks),
                    inline=False
                )
            
            # Create selection view
            view = PlaylistSelectionView(
                self.bot, self.guild_id, self.channel_id,
                playlist_info, entries
            )
            
            # Send as followup message
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error handling playlist: {e}")
            await self.restore_main_control_panel()
            await interaction.followup.send(
                "❌ Failed to process playlist.", 
                ephemeral=True
            )
    
    async def disable_main_control_panel(self, status_message):
        """Disable the main control panel buttons by replacing with DJ-ing message"""
        try:
            # Get guild and voice channel
            guild = self.bot.get_guild(int(self.guild_id))
            voice_channel = guild.get_channel(int(self.channel_id))
            
            # Create DJ-ing embed
            embed = discord.Embed(
                title="🎧 DJ is Working...",
                description=f"Connected to **{voice_channel.name}**\n\n{status_message}\n\n*Please wait...*",
                color=discord.Color.orange()
            )
            
            # Update all control panels with DJ-ing message and no buttons
            for text_channel_id, message_id in list(self.bot.control_panels.items()):
                try:
                    text_channel = guild.get_channel(text_channel_id)
                    if text_channel:
                        message = await text_channel.fetch_message(message_id)
                        await message.edit(embed=embed, view=None)
                except Exception as e:
                    print(f"Error updating control panel to DJ mode: {e}")
                    
        except Exception as e:
            print(f"Error disabling main control panel: {e}")
    
    async def restore_main_control_panel(self):
        """Restore the main control panel with all buttons"""
        try:
            # Update the control panel to show current state with buttons restored
            await self.bot.update_control_panel(self.guild_id, self.channel_id)
        except Exception as e:
            print(f"Error restoring main control panel: {e}")