"""
Enhanced URL Modal for adding songs and playlists - Single input with dynamic playlist selection
"""
import os
import discord
import re
from api_client_youtube.__main__ import ClientYouTube

# Get API key for services
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared YouTube client
youtube_service = ClientYouTube(api_key=YOUTUBE_API_KEY)

class PlaylistSelectionView(discord.ui.View):
    """View for playlist selection after detecting a playlist URL"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries, modal_interaction):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.playlist_info = playlist_info
        self.entries = entries
        self.modal_interaction = modal_interaction
        
        # Add dropdown for quick selection
        self.add_quick_select_dropdown()
        
        # Add custom input for advanced selection
        self.add_item(CustomSelectionButton(bot, guild_id, channel_id, playlist_info, entries, modal_interaction))
    
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
            if interaction.user != self.modal_interaction.user:
                await interaction.response.send_message("Only the person who added the URL can make this selection.", ephemeral=True)
                return
            
            await interaction.response.defer()
            selection = interaction.data['values'][0]
            
            # Process the selection
            await self.process_playlist_with_selection(selection)
            
            # Disable the view
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
        
        select.callback = select_callback
        self.add_item(select)
    
    async def process_playlist_with_selection(self, selection):
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
            
            # Update the message to show processing
            playlist_title = self.playlist_info.get('title', 'Unnamed Playlist')[:90]
            
            embed = discord.Embed(
                title="🔄 Processing Playlist",
                description=f"**{playlist_title}**\nAdding {selection_summary}...",
                color=discord.Color.orange()
            )
            
            await self.modal_interaction.edit_original_response(embed=embed, view=None)
            
            # Process the playlist
            await self.add_tracks_to_queue(selected_indices, playlist_title)
            
        except Exception as e:
            print(f"Error processing playlist selection: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process playlist selection.",
                color=discord.Color.red()
            )
            await self.modal_interaction.edit_original_response(embed=embed, view=None)
    
    async def add_tracks_to_queue(self, selected_indices, playlist_title):
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
                        await self.modal_interaction.edit_original_response(embed=embed)
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
            await self.modal_interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"Error in add_tracks_to_queue: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while adding tracks to the queue.",
                color=discord.Color.red()
            )
            await self.modal_interaction.edit_original_response(embed=embed)

class CustomSelectionButton(discord.ui.Button):
    """Button to open custom selection modal"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries, modal_interaction):
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
        self.modal_interaction = modal_interaction
    
    async def callback(self, interaction):
        if interaction.user != self.modal_interaction.user:
            await interaction.response.send_message("Only the person who added the URL can make this selection.", ephemeral=True)
            return
        
        # Show custom selection modal
        custom_modal = CustomPlaylistSelectionModal(
            self.bot, self.guild_id, self.channel_id, 
            self.playlist_info, self.entries, self.modal_interaction
        )
        await interaction.response.send_modal(custom_modal)

class CustomPlaylistSelectionModal(discord.ui.Modal):
    """Modal for custom playlist selection input"""
    
    def __init__(self, bot, guild_id, channel_id, playlist_info, entries, original_interaction):
        super().__init__(title="Custom Playlist Selection")
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.playlist_info = playlist_info
        self.entries = entries
        self.original_interaction = original_interaction
        
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
            
            # Process the selection
            view = PlaylistSelectionView(
                self.bot, self.guild_id, self.channel_id,
                self.playlist_info, self.entries, self.original_interaction
            )
            await view.process_playlist_with_selection(','.join(str(i+1) for i in selected_indices))
            
        except Exception as e:
            print(f"Error in custom selection: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process custom selection.",
                color=discord.Color.red()
            )
            await self.original_interaction.edit_original_response(embed=embed)

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
            
            # Show processing message
            embed = discord.Embed(
                title="🔄 Processing URL",
                description="Analyzing the YouTube URL...",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Process URL
            result = await youtube_service.process_youtube_url(url)
            
            if not result:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Could not process the URL. The video/playlist might be private, deleted, or region-locked.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            if result['type'] == 'video':
                # Single video - add directly
                await self.handle_single_video(interaction, result)
                
            elif result['type'] == 'playlist':
                # Playlist - show selection interface
                await self.handle_playlist(interaction, result)
            
        except Exception as e:
            print(f"Error processing URL: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await interaction.edit_original_response(embed=embed)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)

    async def handle_single_video(self, interaction, result):
        """Handle single video URL"""
        try:
            video_info = result['info']
            
            # Add to queue
            queue_result = await self.bot.add_to_queue(
                self.guild_id, 
                self.channel_id, 
                video_info['id'], 
                video_info['title']
            )
            
            if queue_result['success']:
                embed = discord.Embed(
                    title="✅ Video Added",
                    description=f"**{video_info['title'][:90]}**",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Failed",
                    description=f"Could not add video: {queue_result.get('message', 'Unknown error')}",
                    color=discord.Color.red()
                )
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"Error handling single video: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process video.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)

    async def handle_playlist(self, interaction, result):
        """Handle playlist URL - show selection interface"""
        try:
            playlist_info = result['info']
            entries = result['entries']
            
            if not entries:
                embed = discord.Embed(
                    title="❌ Empty Playlist",
                    description="The playlist is empty or could not be accessed.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Create playlist selection interface
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
                playlist_info, entries, interaction
            )
            
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error handling playlist: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process playlist.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)