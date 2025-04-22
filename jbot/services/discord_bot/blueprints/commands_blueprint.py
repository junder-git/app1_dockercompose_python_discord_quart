"""
Commands Blueprint for Discord Bot
Handles Discord command registration and processing
"""
import types
import discord
from discord.ext import commands

def apply(bot):
    """
    Apply commands blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Register all commands
    bot.add_command(hello)
    bot.add_command(help_command)
    bot.add_command(search_command)
    
    # Register message handler for "jbot" command
    bot.on_message = types.MethodType(on_message, bot)

# Basic commands
@commands.command(name="hello")
async def hello(ctx):
    """Simple hello command to test the bot is working"""
    # Get cleartimer from bot or default to 10 seconds
    cleartimer = getattr(ctx.bot, 'cleartimer', 10)
    await ctx.send("Hello there!", delete_after=cleartimer)

@commands.command(name="jhelp")
async def help_command(ctx):
    """Show the help information for the bot"""
    embed = discord.Embed(
        title="JBot Music Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="jbot", value="Type this in chat to summon the music control panel", inline=False)
    embed.add_field(name="jbot search <query>", value="Search for a YouTube video and add it to queue", inline=False)
    embed.add_field(name="jbot hello", value="Say hello to the bot", inline=False)
    
    # Get cleartimer from bot or default to 10 seconds
    cleartimer = getattr(ctx.bot, 'cleartimer', 10)
    await ctx.send(embed=embed, delete_after=cleartimer)

@commands.command(name="search")
async def search_command(ctx, *, query):
    """
    Search for a YouTube video and add it to the queue
    
    Args:
        ctx: Command context
        query: Search query string
    """
    # Check if user is in a voice channel
    if not ctx.author.voice:
        cleartimer = getattr(ctx.bot, 'cleartimer', 10)  # Default to 10 seconds if not defined
        await ctx.send("You need to be in a voice channel to use this command", delete_after=cleartimer)
        return
    
    # Validate query length
    if len(query.strip()) < 2:
        cleartimer = getattr(ctx.bot, 'cleartimer', 10)
        await ctx.send("Please provide a more specific search query (at least 2 characters)", delete_after=cleartimer)
        return
    
    voice_channel = ctx.author.voice.channel
    guild_id = str(ctx.guild.id)
    channel_id = str(voice_channel.id)
    
    # Try to search for the video using the shared service
    try:
        # Get the music client
        youtube_client = ctx.bot.youtube_client
        
        # Use the shared MusicService for search
        results = await youtube_client.search_videos(query)
        
        if not results:
            cleartimer = getattr(ctx.bot, 'cleartimer', 10)
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
        
        # Add options to select menu (limit to avoid hitting length limits)
        for i, result in enumerate(results[:5]):
            # Truncate title to fit Discord's label requirements
            title = result['title']
            if len(title) > 90:
                title = title[:87] + "..."
            
            # Get duration
            duration = result.get('duration')
            if duration:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Add to embed
            embed.add_field(
                name=f"{i+1}. {title}",
                value=f"Duration: {duration_str}",
                inline=False
            )
            
            # Add to select menu
            description = f"Duration: {duration_str}"
            if len(description) > 100:
                description = description[:97] + "..."
                
            select.add_option(
                label=f"{i+1}. {title}"[:100],  # Label max length is 100
                value=f"{result['id']}",
                description=description[:100]  # Description max length is 100
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
            result = await ctx.bot.add_to_queue(
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
        cleartimer = getattr(ctx.bot, 'cleartimer', 10)
        await ctx.send(embed=embed, view=view, delete_after=cleartimer)
        
    except Exception as e:
        print(f"Error searching for videos: {e}")
        cleartimer = getattr(ctx.bot, 'cleartimer', 10)
        await ctx.send(f"An error occurred while searching: {str(e)}", delete_after=cleartimer)

async def on_message(self, message):
    """
    Handle incoming messages
    
    Args:
        message: The Discord message object
    """
    # Don't respond to own messages
    if message.author == self.user:
        return
    
    # Process commands first
    await self.process_commands(message)
    
    # Check for the "jbot" trigger word
    if message.content.lower() == "jbot":
        # Check if the user is in a voice channel
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
            
            # Create a response with UI controls (This needs a join_and_show_controls method)
            await self.join_and_show_controls(message.channel, voice_channel, message.guild.id)
        else:
            # Clear timer usually defined at module level, assume 10 seconds if not found
            cleartimer = getattr(self, 'cleartimer', 10)
            await message.channel.send("You need to be in a voice channel first!", delete_after=cleartimer)