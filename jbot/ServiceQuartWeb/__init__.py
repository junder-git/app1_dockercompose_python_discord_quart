"""
Quart Web Service - Main entry point
"""
import os
import sys
from quart import Quart
from quart_discord import DiscordOAuth2Session
from quart_wtf import CSRFProtect
from dotenv import load_dotenv

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import clients
from ClientDiscordBot import DiscordAPIClient
from ClientYoutube import YouTubeClient

# Import core app
from .core.app import create_app

# Create the application
app = create_app()

# Start the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)