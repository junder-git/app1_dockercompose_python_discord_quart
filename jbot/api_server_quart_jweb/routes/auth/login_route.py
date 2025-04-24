"""
Login route for Discord authentication
"""
from quart import session, current_app

async def login_route():
    """
    Login route - redirects to Discord OAuth
    
    Returns:
        str: Redirect URL to Discord OAuth
    """
    # Import discord from current app
    discord = current_app.discord
    
    # Clear any existing session data to ensure a fresh login
    session.clear()
    
    # Make sure we're requesting all the scopes we need
    scope = ["identify", "guilds"]
    authorization_url = await discord.create_session(scope=scope)
    
    return authorization_url