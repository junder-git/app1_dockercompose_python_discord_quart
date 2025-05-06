"""
Core application setup for Quart Web Service
"""
import os
from quart import Quart, render_template
from quart_discord import DiscordOAuth2Session
from quart_wtf import CSRFProtect, CSRFError
from dotenv import load_dotenv

# Import clients
from api_client_discord.__main__ import create_api_client_discord
from api_client_youtube.__main__ import ClientYouTube

# Create CSRF object without binding to app
csrf = CSRFProtect()

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
        SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookie
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
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
    
    # Initialize CSRF protection with the app
    csrf.init_app(app)
    
    # Add CSRF error handler
    @app.errorhandler(CSRFError)
    async def handle_csrf_error(e):
        print(f"CSRF Error: {e.description}")
        return await render_template('error.html', 
                                   error_title="Security Error",
                                   error_message="CSRF token validation failed. Please try again."), 400
    
    # Initialize Discord OAuth
    discord_oauth = DiscordOAuth2Session(app)
    app.discord_oauth = discord_oauth
    
    # Initialize API clients
    app.discord_api_client = create_api_client_discord(
        host="jbot-discord-bot",  # Docker service name
        port=5001,  # Port exposed in Docker
        secret_key=SECRET_KEY
    )
    
    app.youtube_client = ClientYouTube(YOUTUBE_API_KEY)
    
    # Register all route blueprints
    from ..routes import register_blueprints
    register_blueprints(app)
    
    # Exemption for OAuth callback - this is needed
    from ..routes.auth.callback_route import callback_route
    csrf.exempt(callback_route)
    
    # Clean up on app exit
    @app.teardown_appcontext
    async def shutdown_session(exception=None):
        """Clean up resources when the app shuts down"""
        if hasattr(app, 'discord_api_client'):
            await app.discord_api_client.close()
        
        if hasattr(app, 'youtube_client'):
            app.youtube_client.clear_cache()
    
    return app