"""
Route for adding a track to the queue
"""
from quart import redirect, url_for, flash, request, current_app
from ...helpers import login_required
from ...validators.validate_csrf import validate_csrf
from ...validators.validate_queue import validate_add_to_queue

@login_required
async def queue_add_route(guild_id):
    """
    Handle adding videos to the queue
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        Response: Redirect to appropriate page
    """
    await validate_csrf()
    
    discord = current_app.discord
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    
    # Validate form data
    is_valid, errors = await validate_add_to_queue(form)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Get validated data
    channel_id = form.get('channel_id')
    video_id = form.get('video_id')
    video_title = form.get('video_title', 'Unknown video')
    
    # Capture search query parameters to preserve them
    query = form.get('query')
    search_type = form.get('search_type', 'comprehensive')
    playlist_id = form.get('playlist_id')
    page_token = form.get('page_token')
    
    try:
        # Check 1: Is the user in a voice channel?
        user = await discord.fetch_user()
        user_id = str(user.id)
        user_voice_state = await discord_client.get_user_voice_state(guild_id, user_id)
        
        if not user_voice_state or not user_voice_state.get('channel_id'):
            flash("You need to join a voice channel before adding music", "warning")
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
        
        # Check 2: Get the current queue to see if the bot is connected
        queue_info = await discord_client.get_queue(guild_id, channel_id)
        
        # If bot is not connected to the channel, tell user to use Discord command
        if not queue_info.get('is_connected', False):
            flash("Bot is not connected to your voice channel. Type 'jbot' in a Discord text channel first to connect the bot.", "warning")
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
        
        # Check 3: Make sure bot and user are in the same channel
        if user_voice_state.get('channel_id') != channel_id:
            flash("You must be in the same voice channel as the bot to add music", "warning")
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
        
        # Now add to queue using the Discord bot API
        result = await discord_client.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result.get('success'):
            flash(f"Added '{video_title}' to queue", "success")
        else:
            flash(f"Error adding to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error adding to queue: {str(e)}", "error")
    
    # Redirect back to the search page with the same parameters
    redirect_params = {'guild_id': guild_id}
    if query:
        redirect_params['query'] = query
    if search_type:
        redirect_params['search_type'] = search_type
    if playlist_id:
        redirect_params['playlist_id'] = playlist_id
    if page_token:
        redirect_params['page_token'] = page_token
        
    return redirect(url_for('search.youtube_search_route', **redirect_params))