from functools import wraps
from quart import Quart
import os
from dotenv import load_dotenv
from Class_DiscordBotAPI import DiscordBotAPI
from Class_YouTube import YouTubeService
from Class_MusicPlayer import MusicService
import werkzeug.security
import secrets
from quart_wtf import QuartWTF, CSRFProtect  # Update import
from quart_discord import DiscordOAuth2Session

# Import routes package
from routes import register_blueprints

# First try loading .env.local, then fall back to .env if needed
load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Required for OAuth 2 over http
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Initialize the services
youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)
music_service = MusicService(api_key=YOUTUBE_API_KEY)

# Initialize the Bot API client
bot_api = DiscordBotAPI(
    host="discord-bot",  # Docker service name
    port=5001,           # Port exposed in docker-compose
    secret_key=os.environ.get('SECRET_KEY')
)

app = Quart(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["DISCORD_CLIENT_ID"] = os.environ.get('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.environ.get('DISCORD_CLIENT_SECRET')
app.config["DISCORD_REDIRECT_URI"] = os.environ.get('DISCORD_REDIRECT_URI')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Discord OAuth
discord = DiscordOAuth2Session(app)

# Make discord and bot_api available to all routes
app.discord = discord
app.bot_api = bot_api
app.quart_app = app  # For render_template access in blueprints
app.music_service = music_service
app.youtube_service = youtube_service

# Register all route blueprints
register_blueprints(app)

# Add cleanup on app exit
@app.teardown_appcontext
async def shutdown_session(exception=None):
    await bot_api.close()

@app.before_serving
async def before_serving():
    """Initialize resources before the server starts"""
    # Nothing to initialize yet

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)