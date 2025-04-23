"""
Enhanced URL Modal for adding songs and playlists
"""
import os
import discord
from jbot.ClientYoutube.__main__ import YouTubeClient

# Get API key for services
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared YouTube client
youtube_service = YouTubeClient(api_key=YOUTUBE_API_KEY)

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
            result = await youtube_service.process_youtube_url(url)
            
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