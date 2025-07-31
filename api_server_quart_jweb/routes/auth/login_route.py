"""
Login route for current_app.discord_oauth authentication
"""
from quart import session, current_app

async def login_route():
    """
    Login route - redirects to current_app.discord_oauth OAuth
    
    Returns:
        str: Redirect URL to current_app.discord_oauth OAuth
    """
    
    # Clear any existing session data to ensure a fresh login
    session.clear()
    
    # Make sure we're requesting all the scopes we need
    scope = ["identify", "guilds"]
    authorization_url = await current_app.discord_oauth.create_session(scope=scope)
    
    return authorization_url