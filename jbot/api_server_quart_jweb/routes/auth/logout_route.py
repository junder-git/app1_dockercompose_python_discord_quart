"""
Logout route for current_app.discord_oauth authentication
"""
from quart import session, current_app, redirect, url_for

async def logout_route():
    """
    Logout route - clears session and revokes current_app.discord_oauth token
    
    Returns:
        Response: Redirect to home page
    """
    
    # Revoke the token with current_app.discord_oauth if possible
    if current_app.discord_oauth.authorized:
        try:
            await current_app.discord_oauth.revoke()
        except:
            pass
    
    # Clear the session
    session.clear()
    
    # Redirect to the home page
    return redirect(url_for("dashboard.index_route"))