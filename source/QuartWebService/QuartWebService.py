from functools import wraps
from quart import Quart
import os
from dotenv import load_dotenv
from quart_wtf import CSRFProtect  # Update import
from quart_discord import DiscordOAuth2Session

# Import discord API client blueprint
from additional_clients.discord_api_client import discord_api_client_bp, create_discord_bot_api

# Import YouTube API client
from additional_clients.youtube_api_client import YouTubeService

# Import routes package
from routes import register_blueprints

# First try loading .env.local, then fall back to .env if needed
load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Required for OAuth 2 over http
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

app = Quart(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["DISCORD_CLIENT_ID"] = os.environ.get('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.environ.get('DISCORD_CLIENT_SECRET')
app.config["DISCORD_REDIRECT_URI"] = os.environ.get('DISCORD_REDIRECT_URI')

# Initialize the Bot API client using the new blueprint factory function
app.bot_api = create_discord_bot_api(
    host="discord-bot",  # Docker service name
    port=5001,           # Port exposed in docker-compose
    secret_key=os.environ.get('SECRET_KEY')
)

# Initialize YouTube service and make it available to routes
app.youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)

# Register the discord_api_client blueprint
app.register_blueprint(discord_api_client_bp)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Discord OAuth
discord = DiscordOAuth2Session(app)

# Make discord and bot_api available to all routes
app.discord = discord
app.quart_app = app  # For render_template access in blueprints

# Register all route blueprints
register_blueprints(app)

# Add cleanup on app exit
@app.teardown_appcontext
async def shutdown_session(exception=None):
    await app.bot_api.close()

@app.before_serving
async def before_serving():
    """Initialize resources before the server starts"""
    # Nothing to initialize yet

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)