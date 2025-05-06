"""
Bot join route - handles joining a voice channel
"""
from quart import redirect, url_for, current_app, flash, request
from ...routes.auth.login_required import login_required

@login_required
async def bot_join_route(guild_id):
    """
    Handle a request to make the bot join a voice channel
    
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
    
    # Get user's voice channel
    user = await current_app.discord_oauth.fetch_user()
    user_id = str(user.id)
    user_voice_state = await current_app.discord_api_client.get_user_voice_state(guild_id, user_id)
    
    # If user is not in the selected voice channel, show error
    if not user_voice_state or user_voice_state.get('channel_id') != channel_id:
        flash("You must be in the voice channel to connect the bot", "warning")
        return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Tell the bot to join the channel
    result = await current_app.discord_api_client.join_voice_channel(guild_id, channel_id)
    
    if result.get('success'):
        flash("Connected to voice channel", "success")
    else:
        flash(f"Error connecting to voice channel: {result.get('error', 'Unknown error')}", "error")
    
    # Redirect back to the server dashboard
    return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))