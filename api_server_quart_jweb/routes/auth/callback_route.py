"""
Callback route for current_app.discord_oauth OAuth2
"""
import traceback
from quart import session, current_app, redirect, url_for

async def callback_route():
    """
    Callback route for current_app.discord_oauth OAuth
    
    Returns:
        Response: Redirect to dashboard or home page
    """
    
    try:
        # Complete the OAuth flow
        data = await current_app.discord_oauth.callback()
        
        # Get the user
        user = await current_app.discord_oauth.fetch_user()
        
        # Store user information in session
        session['user_id'] = user.id
        session['username'] = user.name
        
        # Also store the access token for further API calls
        if hasattr(current_app.discord_oauth, 'token'):
            session['current_app.discord_oauth_token'] = current_app.discord_oauth.token
        
        # Print debug information
        print(f"OAuth callback successful for user: {user.name} ({user.id})")
        print(f"Session after callback: {list(session.keys())}")
        
        # Fetch user guilds to verify API access is working
        try:
            guilds = await current_app.discord_oauth.fetch_guilds()
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
        return redirect(url_for("dashboard.index_route"))