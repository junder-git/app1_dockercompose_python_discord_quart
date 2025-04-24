"""
Logout route for Discord authentication
"""
from quart import session, current_app, redirect, url_for

async def logout_route():
    """
    Logout route - clears session and revokes Discord token
    
    Returns:
        Response: Redirect to home page
    """
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
    return redirect(url_for("dashboard.index_route"))