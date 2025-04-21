"""
search_command method for Discord bot
Handles the search command to find YouTube videos
"""
import discord

async def search_command(self, ctx, *, query):
    """
    Search for a YouTube video and add it to the queue
    
    Args:
        ctx: Command context
        query: Search query string
    """
    # Check if user is in a voice channel
    if not ctx.author.voice:
        cleartimer = getattr(self, 'cleartimer', 10)  # Default to 10 seconds if not defined
        await ctx.send("You need to be in a voice channel to use this command", delete_after=cleartimer)
        return
    
    # Validate query length
    if len(query.strip()) < 2:
        cleartimer = getattr(self, 'cleartimer', 10)
        await ctx.send("Please provide a more specific search query (at least 2 characters)", delete_after=cleartimer)
        return
    
    voice_channel = ctx.author.voice.channel
    guild_id = str(ctx.guild.id)
    channel_id = str(voice_channel.id)
    
    # Try to search for the video using the shared service
    try:
        # Get the MusicService instance
        music_service = getattr(self, 'music_service', None)
        if not music_service:
            from source.Shared.Class_MusicPlayer import MusicService
            import os
            YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
            self.music_service = MusicService(api_key=YOUTUBE_API_KEY)
            music_service = self.music_service
        
        # Use the shared MusicService for optimized search
        results = await music_service.search_videos(query)
        
        if not results:
            cleartimer = getattr(self, 'cleartimer', 10)
            await ctx.send(f"No results found for: {query}", delete_after=cleartimer)
            return
        
        # Create embed for results
        embed = discord.Embed(
            title=f"Search Results for: {query}",
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
                description=f"Duration: {duration_str}"[:100]  # Description max length is 100
            )
        
        # Create view and add select
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        
        # Define select callback
        async def select_callback(interaction):
            # Ensure the user who invoked the command is making the selection
            if interaction.user != ctx.author:
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
            result = await self.add_to_queue(
                guild_id, 
                channel_id, 
                selected_track['id'], 
                selected_track['title']
            )
            
            # Confirm selection
            await interaction.followup.send(
                f"Added to queue: **{selected_track['title']}**",
                ephemeral=True
            )
        
        # Assign callback
        select.callback = select_callback
        
        # Send results
        cleartimer = getattr(self, 'cleartimer', 10)
        await ctx.send(embed=embed, view=view, delete_after=cleartimer)
        
    except Exception as e:
        print(f"Error searching for videos: {e}")
        cleartimer = getattr(self, 'cleartimer', 10)
        await ctx.send(f"An error occurred while searching: {str(e)}", delete_after=cleartimer)