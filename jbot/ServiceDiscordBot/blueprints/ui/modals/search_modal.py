"""
Search Modal for the Discord Bot
"""
import os
import discord
from ClientYoutube import YouTubeClient

# Get API key for services
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared services
youtube_service = YouTubeClient(api_key=YOUTUBE_API_KEY)

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
            results = await youtube_service.search_videos(self.query.value)
            
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