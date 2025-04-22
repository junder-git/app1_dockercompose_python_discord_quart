"""
Index Blueprint for Quart Web Service
Handles the home page and other static pages
"""
from quart import Blueprint, render_template, session, current_app, redirect, url_for

# Create blueprint
index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
async def index_route():
    """Home page route"""
    # Check if user is logged in
    if 'user_id' in session:
        # Redirect to dashboard if already logged in
        return redirect(url_for('dashboard.dashboard_route'))
    
    # Get Discord instance
    discord = current_app.discord
    
    # Render the index template
    return await render_template('index.html', authorized=await discord.authorized)