#!/usr/bin/env python
"""
Migration script to help modularize the Discord bot codebase.
This script creates the directory structure and skeleton files for the modular architecture.
"""
import os
import re
import shutil
import sys

def ensure_dir(directory):
    """Ensure directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_file(path, content):
    """Create a file with the given content"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

def create_directory_structure():
    """Create the required directory structure"""
    # Create main directories
    dirs = [
        "jbot/ServiceDiscordBot/core",
        "jbot/ServiceDiscordBot/utils",
        "jbot/ServiceDiscordBot/blueprints",
    ]
    
    # Create blueprint directories
    blueprints = ["api", "commands", "events", "playback", "queue", "voice", "ui"]
    for blueprint in blueprints:
        dirs.append(f"jbot/ServiceDiscordBot/blueprints/{blueprint}")
        
        # Add subdirectories for specific blueprints
        if blueprint == "api":
            dirs.append(f"jbot/ServiceDiscordBot/blueprints/{blueprint}/handlers")
        elif blueprint == "ui":
            dirs.append(f"jbot/ServiceDiscordBot/blueprints/{blueprint}/components")
            dirs.append(f"jbot/ServiceDiscordBot/blueprints/{blueprint}/modals")
            dirs.append(f"jbot/ServiceDiscordBot/blueprints/{blueprint}/helpers")
            
    # Create all directories
    for directory in dirs:
        ensure_dir(directory)
        # Create __init__.py in each directory
        init_path = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_path):
            create_file(init_path, '"""Module initialization"""\n')

def extract_methods_from_file(file_path, blueprint_name):
    """
    Extract methods from the given file that belong to the specified blueprint.
    Returns a dictionary of method_name -> (method_content, method_description)
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    try:
        # Try reading with UTF-8 encoding first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # If UTF-8 fails, try with a fallback encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
    
    # Find the apply function for this blueprint
    apply_pattern = r'def apply\(bot\):(.*?)(?=def|$)'
    apply_match = re.search(apply_pattern, content, re.DOTALL)
    
    if not apply_match:
        print(f"Could not find apply function in {file_path}")
        return {}
    
    apply_content = apply_match.group(1)
    
    # Extract methods bound to the bot
    method_names = []
    for line in apply_content.split('\n'):
        match = re.search(r'bot\.(\w+)\s*=\s*types\.MethodType\((\w+)', line)
        if match:
            method_names.append(match.group(2))
    
    # Extract each method's content
    methods = {}
    for method_name in method_names:
        method_pattern = fr'def {method_name}\(self,.*?\):(.*?)(?=def|$)'
        method_match = re.search(method_pattern, content, re.DOTALL)
        
        if method_match:
            # Find docstring if it exists
            method_content = method_match.group(0)
            docstring_pattern = r'"""(.*?)"""'
            docstring_match = re.search(docstring_pattern, method_content, re.DOTALL)
            
            if docstring_match:
                description = docstring_match.group(1).strip()
            else:
                description = f"Function for {method_name}"
            
            methods[method_name] = (method_content, description)
        else:
            print(f"Could not find method content for {method_name}")
    
    return methods

def create_method_file(method_name, method_content, description, blueprint_dir):
    """Create a file for a specific method"""
    file_path = os.path.join(blueprint_dir, f"{method_name}.py")
    
    # Basic file template
    file_content = f'''"""
{description}
"""

{method_content}
'''
    create_file(file_path, file_content)

def create_blueprint_init(blueprint_name, method_names):
    """Create the __init__.py file for a blueprint"""
    blueprint_dir = f"jbot/ServiceDiscordBot/blueprints/{blueprint_name}"
    
    # Import statements
    imports = '\n'.join([f"from .{method} import {method}" for method in method_names])
    
    # Method type assignments
    assignments = '\n    '.join([f"bot.{method} = types.MethodType({method}, bot)" for method in method_names])
    
    content = f'''"""
{blueprint_name.title()} Blueprint for Discord Bot
"""
import types
{imports}

def apply(bot):
    """
    Apply {blueprint_name} blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind {blueprint_name} methods to the bot
    {assignments}
'''
    
    create_file(os.path.join(blueprint_dir, "__init__.py"), content)

def create_main_blueprint_init():
    """Create the main blueprints/__init__.py file"""
    content = '''"""
Blueprints package for Discord Bot Service
"""
from .api import apply as api_blueprint
from .commands import apply as commands_blueprint
from .events import apply as events_blueprint
from .queue import apply as queue_blueprint
from .playback import apply as playback_blueprint
from .voice import apply as voice_blueprint
from .ui import apply as ui_blueprint

__all__ = [
    'api_blueprint',
    'commands_blueprint',
    'events_blueprint',
    'queue_blueprint',
    'playback_blueprint',
    'voice_blueprint',
    'ui_blueprint'
]
'''
    create_file("jbot/ServiceDiscordBot/blueprints/__init__.py", content)

def create_main_init():
    """Create the main __init__.py file"""
    content = '''"""
Discord Bot Service - Main entry point
"""
import os
import sys
import discord
from discord.ext import commands
from collections import defaultdict
from dotenv import load_dotenv

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import clients
from clients.ClientYoutube import YouTubeClient

# Import core bot class
from .core.bot import JBotDiscord

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

# Create the bot instance
bot = JBotDiscord(command_prefix="jbot ", intents=intents)

# Apply all blueprints
bot.apply_blueprints()

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
'''
    create_file("jbot/ServiceDiscordBot/__init__.py", content)

def create_bot_class():
    """Create the bot class file"""
    content = '''"""
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
    queue_blueprint,
    playback_blueprint,
    voice_blueprint,
    ui_blueprint
)

# Import clients
from clients.ClientYoutube import YouTubeClient

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
        queue_blueprint(self)
        playback_blueprint(self)
        voice_blueprint(self)
        ui_blueprint(self)
'''
    ensure_dir("jbot/ServiceDiscordBot/core")
    create_file("jbot/ServiceDiscordBot/core/bot.py", content)
    create_file("jbot/ServiceDiscordBot/core/__init__.py", '"""Core bot module"""\n')

def process_blueprint(blueprint_name, source_file):
    """Process a blueprint file and extract its methods"""
    print(f"Processing {blueprint_name} blueprint from {source_file}")
    
    # Extract methods
    methods = extract_methods_from_file(source_file, blueprint_name)
    
    # Create directory for blueprint
    blueprint_dir = f"jbot/ServiceDiscordBot/blueprints/{blueprint_name}"
    ensure_dir(blueprint_dir)
    
    # Create a file for each method
    for method_name, (method_content, description) in methods.items():
        create_method_file(method_name, method_content, description, blueprint_dir)
    
    # Create blueprint init file
    create_blueprint_init(blueprint_name, list(methods.keys()))
    
    print(f"Completed {blueprint_name} blueprint with {len(methods)} methods")

def main():
    """Main execution function"""
    print("Starting Discord Bot modularization...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create main blueprint init
    create_main_blueprint_init()
    
    # Create main init file
    create_main_init()
    
    # Create bot class
    create_bot_class()
    
    # Blueprint source file mapping
    blueprint_files = {
        "api": "jbot/ServiceDiscordBot/api.py",
        "events": "jbot/ServiceDiscordBot/events.py",
        "playback": "jbot/ServiceDiscordBot/playback.py",
        "queue": "jbot/ServiceDiscordBot/queue.py",
        "voice": "jbot/ServiceDiscordBot/voice.py",
        "ui": "jbot/ServiceDiscordBot/ui.py",
        # Add commands blueprint here when available
    }
    
    # Process each blueprint
    for blueprint_name, source_file in blueprint_files.items():
        process_blueprint(blueprint_name, source_file)
    
    print("\nModularization complete!")
    print("\nNext steps:")
    print("1. Check the generated files for accuracy")
    print("2. Complete any remaining manual tasks")
    print("3. Test the modularized bot")

if __name__ == "__main__":
    main()