"""
Index route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, session, render_template, current_app

# Create a blueprint for index route
index_bp = Blueprint('index', __name__)

@index_bp.route("/")
async def index_route():
    """Home page route"""
    # Import discord from QuartApp context to avoid circular imports
    discord = current_app.discord
    
    # Redirect to dashboard if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_route'))
    
    return await render_template(
        "index.html", 
        authorized=await discord.authorized
    )