"""
Core Discord bot class
"""
import os
from collections import defaultdict
import discord
from discord.ext import commands

# Import blueprint registration
from ..blueprints import (
    api_blueprint,
    commands_blueprint,
    events_blueprint,
    ui_blueprint
)

# Import clients
from api_client_youtube.__main__ import ClientYouTube

class JBotDiscord(commands.Bot):
    """Main Discord bot class"""
    def __init__(self, *args, **kwargs):
        """
        Initialize the bot with custom attributes and configurations
        
        Args:
            *args: Positional arguments for the base Bot class
            **kwargs: Keyword arguments for the base Bot class
        """
        # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)
        
        # Set secret key from environment
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        
        # Initialize API server attribute
        self.api_server = None
        
        # Initialize YouTube client
        self.youtube_client = ClientYouTube(
            api_key=os.environ.get('YOUTUBE_API_KEY')
        )
        
        # Music queue management
        self.music_queues = defaultdict(list)  # Queue ID -> list of tracks
        self.currently_playing = {}  # Queue ID -> current track info
        self.voice_connections = {}  # Queue ID -> voice client
        
        # UI and control panel tracking
        self.control_panels = {}  # Channel ID -> Message ID
        self.playlist_processing = {}  # Queue ID -> boolean flag to interrupt playlist processing
        
        # Message auto-deletion time (in seconds)
        self.cleartimer = 10
    
    def get_queue_id(self, guild_id, channel_id):
        """
        Create a unique queue ID from guild and channel IDs
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
        
        Returns:
            str: Unique queue identifier
        """
        return f"{guild_id}_{channel_id}"
    
    def apply_blueprints(self):
        """
        Apply functional blueprints to the bot
        
        This method registers all command handlers, event listeners, 
        and UI components for the bot
        """
        # Apply each blueprint in order
        api_blueprint(self)      # API endpoint handlers
        commands_blueprint(self)  # Text and slash commands
        events_blueprint(self)    # Bot lifecycle and event handlers
        ui_blueprint(self)        # User interface components
    
    async def setup_hook(self):
        """Called when the bot starts up"""
        # Start the API server (if the method exists from blueprints)
        if hasattr(self, 'start_api_server'):
            await self.start_api_server()
            print("API server started")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")