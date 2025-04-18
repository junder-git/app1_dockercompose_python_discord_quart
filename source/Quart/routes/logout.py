"""
Logout route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, session

# Create a blueprint for logout route
logout_bp = Blueprint('logout', __name__)

@logout_bp.route("/logout")
async def logout_route():
    """Logout route - clears session and revokes Discord token"""
    from quart import current_app
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