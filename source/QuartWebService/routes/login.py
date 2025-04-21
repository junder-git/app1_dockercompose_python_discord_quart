"""
Login route for JBot Quart application
"""
from quart import Blueprint, session, current_app

# Create a blueprint for login route
login_bp = Blueprint('login', __name__)

@login_bp.route("/login")
async def login_route():
    """Login route - redirects to Discord OAuth"""
    # Import discord from QuartApp context
    discord = current_app.discord
    
    # Clear any existing session data to ensure a fresh login
    session.clear()
    
    # Make sure we're requesting all the scopes we need
    scope = ["identify", "guilds"]
    authorization_url = await discord.create_session(scope=scope)
    
    return authorization_url