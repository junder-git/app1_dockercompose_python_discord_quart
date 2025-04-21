"""
Discord Bot Service for JBot
Main bot file that initializes the bot and registers all methods
"""
import sys
import os
# Add the current directory to Python path
sys.path.append(os.getcwd())
import discord
from discord.ext import commands
from collections import defaultdict
from dotenv import load_dotenv
from additional_clients.youtube_api_client import YouTubeService
from additional_clients.music_player_client import MusicService

# Import methods package that contains all bot methods
from methods import apply_methods

# First try loading .env.local, then fall back to .env if needed
load_dotenv()

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared services
youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)
music_service = MusicService(api_key=YOUTUBE_API_KEY)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, *args, SECRET_KEY=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.SECRET_KEY = SECRET_KEY
        self.api_server = None
        
        # Music queue handling - rename attribute to avoid conflicts
        self.music_queues = defaultdict(list)  # Queue ID -> list of tracks
        self.currently_playing = {}  # Queue ID -> current track info
        self.voice_connections = {}  # Queue ID -> voice client
        
        # Track control panels sent to text channels
        self.control_panels = {}  # Channel ID -> Message ID
        self.playlist_processing = {}  # Queue ID -> boolean flag to interrupt playlist processing
        
        # Set shared services
        self.youtube_service = youtube_service
        self.music_service = music_service
        
        # Set cleartimer for auto-delete messages
        self.cleartimer = 10
    
    # Define the setup_hook method directly in the class
    async def setup_hook(self):
        """
        This is called when the bot starts up
        """
        # Start the API server
        await self.start_api_server()
        print("API server started")

# BOT COMMANDS

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
cleartimer = 10

# Create the bot instance
bot = MyBot(command_prefix="jbot ", intents=intents, SECRET_KEY=SECRET_KEY)

# Apply all methods from the methods package
apply_methods(bot)

# Register commands
@bot.command(name="hello")
async def hello(ctx):
    """Simple hello command to test the bot is working"""
    await ctx.send("Hello there!", delete_after=cleartimer)

@bot.command(name="jhelp")
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
    
    await ctx.send(embed=embed, delete_after=cleartimer)

# Note: The search_command is now imported from methods/commands/search_command.py
# It's registered below to attach it to the bot

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)