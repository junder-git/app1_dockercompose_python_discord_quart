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
from ClientYoutube import YouTubeClient

class JBotDiscord(commands.Bot):
    """Main Discord bot class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.api_server = None
        
        # Initialize clients
        self.youtube_client = YouTubeClient(api_key=os.environ.get('YOUTUBE_API_KEY'))
        
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
        ui_blueprint(self)