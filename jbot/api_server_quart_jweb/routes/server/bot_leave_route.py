"""
Bot leave route - handles leaving a voice channel
"""
from quart import redirect, url_for, current_app, flash, request, session
from ...routes.auth.login_required import login_required

@login_required
async def bot_leave_route(guild_id):
    """
    Handle a request to make the bot leave a voice channel
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: Redirect to server dashboard
    """
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("User not authenticated", "error")
        return redirect(url_for('auth.login_route'))
    
    # Use the disconnect_voice_channel method instead of leave_voice_channel
    result = await current_app.discord_api_client.disconnect_voice_channel(guild_id, user_id)
    
    if result.get('success'):
        flash("Disconnected from voice channel", "success")
    else:
        flash(f"Error disconnecting from voice channel: {result.get('error', 'Unknown error')}", "error")
    
    # Redirect back to the server dashboard
    return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))