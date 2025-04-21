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
from clients.discord_api import DiscordAPIClient, discord_api_blueprint
from clients.youtube_api import YouTubeClient, youtube_api_blueprint
from clients.music_player import MusicPlayerClient, music_player_blueprint

# Import blueprints
from quart_web.blueprints import (
    index_blueprint,
    auth_blueprint,
    dashboard_blueprint,
    server_blueprint,
    search_blueprint,
    queue_blueprint
)

# Load environment variables
load_dotenv()

# Configure the app and its dependencies
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Required for OAuth2 over http in development

# Get environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Create the Quart app
app = Quart(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    DISCORD_CLIENT_ID=DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET=DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI=DISCORD_REDIRECT_URI,
    SESSION_COOKIE_SAMESITE='Lax',  # Important for OAuth redirect
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max upload size
)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Discord OAuth
discord = DiscordOAuth2Session(app)
app.discord = discord

# Initialize API clients
app.discord_client = DiscordAPIClient(
    host="discord-bot",  # Docker service name
    port=5001,  # Port exposed in Docker
    secret_key=SECRET_KEY
)

app.youtube_client = YouTubeClient(api_key=YOUTUBE_API_KEY)
app.music_client = MusicPlayerClient(api_key=YOUTUBE_API_KEY)

# Register client blueprints
app.register_blueprint(discord_api_blueprint)
app.register_blueprint(youtube_api_blueprint)
app.register_blueprint(music_player_blueprint)

# Register application blueprints
app.register_blueprint(index_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(server_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(queue_blueprint)

# Clean up on app exit
@app.teardown_appcontext
async def shutdown_session(exception=None):
    """Clean up resources when the app shuts down"""
    if hasattr(app, 'discord_client'):
        await app.discord_client.close()
    
    if hasattr(app, 'youtube_client'):
        app.youtube_client.clear_cache()
    
    if hasattr(app, 'music_client'):
        await app.music_client.close()

# Start the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)