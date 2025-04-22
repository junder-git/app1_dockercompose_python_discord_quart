"""
Auth Blueprint for Quart Web Service
Handles authentication-related routes
"""
from quart import Blueprint, session, current_app, redirect, url_for
import traceback
from quart_wtf import CSRFProtect

# Create blueprint
auth_blueprint = Blueprint('auth', __name__)

# Get CSRF protection
csrf = CSRFProtect()

@auth_blueprint.route("/login")
async def login_route():
    """Login route - redirects to Discord OAuth"""
    # Import discord from current app
    discord = current_app.discord
    
    # Clear any existing session data to ensure a fresh login
    session.clear()
    
    # Make sure we're requesting all the scopes we need
    scope = ["identify", "guilds"]
    authorization_url = await discord.create_session(scope=scope)
    
    return authorization_url

@auth_blueprint.route("/logout")
async def logout_route():
    """Logout route - clears session and revokes Discord token"""
    discord = current_app.discord
    
    # Revoke the token with Discord if possible
    if discord.authorized:
        try:
            await discord.revoke()
        except:
            pass
    
    # Clear the session
    session.clear()
    
    # Redirect to the home page
    return redirect(url_for("index.index_route"))

# The callback route is exempt from CSRF protection
@auth_blueprint.route("/callback")
@csrf.exempt
async def callback_route():
    """Callback route for Discord OAuth"""
    discord = current_app.discord
    
    try:
        # Complete the OAuth flow
        data = await discord.callback()
        
        # Get the user
        user = await discord.fetch_user()
        
        # Store user information in session
        session['user_id'] = user.id
        session['username'] = user.name
        
        # Also store the access token for further API calls
        if hasattr(discord, 'token'):
            session['discord_token'] = discord.token
        
        # Print debug information
        print(f"OAuth callback successful for user: {user.name} ({user.id})")
        print(f"Session after callback: {list(session.keys())}")
        
        # Fetch user guilds to verify API access is working
        try:
            guilds = await discord.fetch_guilds()
            print(f"Successfully fetched {len(guilds)} guilds for user")
        except Exception as e:
            print(f"Error fetching guilds: {e}")
        
        return redirect(url_for("dashboard.dashboard_route"))
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        # Log the full traceback for better debugging
        traceback.print_exc()
        # Clear the session on error to prevent loops
        session.clear()
        return redirect(url_for("index.index_route"))