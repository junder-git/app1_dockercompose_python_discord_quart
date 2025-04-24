"""
Index route for home page
"""
from quart import render_template, session, current_app, redirect, url_for

async def index_route():
    """
    Home page route
    
    Returns:
        Response: Rendered index template or redirect to dashboard
    """
    # Check if user is logged in
    if 'user_id' in session:
        # Redirect to dashboard if already logged in
        return redirect(url_for('dashboard.dashboard_route'))
    
    # Get Discord instance
    discord = current_app.discord
    
    # Render the index template
    return await render_template('index.html', authorized=await discord.authorized)