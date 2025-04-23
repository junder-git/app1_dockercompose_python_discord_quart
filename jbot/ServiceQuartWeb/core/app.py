"""
Core application setup for Quart Web Service
"""
import os
from quart import Quart
from quart_discord import DiscordOAuth2Session
from quart_wtf import CSRFProtect
from dotenv import load_dotenv

# Import clients
import jbot.ClientDiscordBot.__main__ as __main__
import jbot.ClientYoutube.__main__ as __main__

def create_app():
    """Create and configure the Quart application"""
    # Load environment variables
    load_dotenv()
    
    # Configure OAuth2 for development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    # Get environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
    DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    
    # Create the Quart app
    app = Quart(__name__, template_folder='../templates', static_folder='../static')
    
    # Configure app
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        DISCORD_CLIENT_ID=DISCORD_CLIENT_ID,
        DISCORD_CLIENT_SECRET=DISCORD_CLIENT_SECRET,
        DISCORD_REDIRECT_URI=DISCORD_REDIRECT_URI,
        SESSION_COOKIE_SAMESITE='Lax',  # Important for OAuth redirect
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload size
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_CHECK_DEFAULT=True,
        WTF_CSRF_METHODS=["POST", "PUT", "PATCH", "DELETE"],
        WTF_CSRF_TIME_LIMIT=3600,
        WTF_CSRF_FIELD_NAME="csrf_token",
        WTF_CSRF_HEADERS=["X-CSRFToken", "X-CSRF-Token"],
        WTF_CSRF_SSL_STRICT=True,
        WTF_CSRF_SECRET_KEY=SECRET_KEY
    )
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize Discord OAuth
    discord = DiscordOAuth2Session(app)
    app.discord = discord
    
    # Initialize API clients
    app.discord_client = __main__(
        host="jbot-discord-bot",  # Docker service name
        port=5001,  # Port exposed in Docker
        secret_key=SECRET_KEY
    )
    
    app.youtube_client = __main__(api_key=YOUTUBE_API_KEY)
    
    # Register all route blueprints
    from ..routes import register_blueprints
    register_blueprints(app)
    
    # Clean up on app exit
    @app.teardown_appcontext
    async def shutdown_session(exception=None):
        """Clean up resources when the app shuts down"""
        if hasattr(app, 'discord_client'):
            await app.discord_client.close()
        
        if hasattr(app, 'youtube_client'):
            app.youtube_client.clear_cache()
    
    return app