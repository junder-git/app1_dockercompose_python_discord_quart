"""
Main entry point for the Discord Bot Service
"""
import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the bot class
from ServiceDiscordBot.core.bot import JBotDiscord

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

def main():
    """
    Main function to run the Discord bot
    """
    # Create the bot instance
    bot = JBotDiscord(command_prefix="jbot ", intents=intents)

    # Apply all blueprints
    bot.apply_blueprints()

    # Run the bot
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()