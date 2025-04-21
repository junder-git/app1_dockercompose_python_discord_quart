"""
Discord Bot Service - Main entry point
"""
import os
import sys
import asyncio
import discord
from discord.ext import commands
from collections import defaultdict
from dotenv import load_dotenv
import aiohttp
from aiohttp import web

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import clients
from clients.youtube_api import YouTubeClient
from clients.music_player import MusicPlayerClient

# Import blueprints
from discord_bot.blueprints import (
    api_blueprint,
    commands_blueprint,
    events_blueprint,
    queue_blueprint,
    playback_blueprint,
    voice_blueprint
)

# Load environment variables
load_dotenv()

# Get configuration from environment
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
API_PORT = int(os.environ.get('DISCORD_BOT_API_PORT', 5001))

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

class JBotDiscord(commands.Bot):
    """Main Discord bot class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SECRET_KEY = SECRET_KEY
        self.api_server = None
        
        # Initialize clients
        self.youtube_client = YouTubeClient(api_key=YOUTUBE_API_KEY)
        self.music_client = MusicPlayerClient(api_key=YOUTUBE_API_KEY)
        
        # Music queue handling
        self.music_queues = defaultdict(list)  # Queue ID -> list of tracks
        self.currently_playing = {}  # Queue ID -> current track info
        self.voice_connections = {}  # Queue ID -> voice client
        
        # Track control panels sent to text channels
        self.control_panels = {}  # Channel ID -> Message ID
        self.playlist_processing = {}  # Queue ID -> boolean flag to interrupt playlist processing
        
        # Message auto-deletion time (in seconds)
        self.cleartimer = 10
    
    def get_queue_id(self, guild_id, channel_id):
        """Create a unique queue ID from guild and channel IDs"""
        return f"{guild_id}_{channel_id}"
    
    def apply_blueprints(self):
        """Apply functional blueprints to the bot"""
        # Apply each blueprint 
        api_blueprint(self)
        commands_blueprint(self)
        events_blueprint(self)
        queue_blueprint(self)
        playback_blueprint(self)
        voice_blueprint(self)

# Create the bot instance
bot = JBotDiscord(command_prefix="jbot ", intents=intents)

# Apply all blueprints
bot.apply_blueprints()

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)