"""
Discord Bot Service - Main entry point
"""
import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Explicitly add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import clients
import ClientYoutube

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

def run():
    """
    Function to run the bot
    """
    # Create the bot instance
    bot = JBotDiscord(command_prefix="jbot ", intents=intents)

    # Apply all blueprints
    bot.apply_blueprints()

    # Run the bot
    bot.run(DISCORD_BOT_TOKEN)

# Ensure the bot can be run as a module
if __name__ == "__main__":
    run()