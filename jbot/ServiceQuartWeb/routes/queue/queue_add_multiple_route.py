"""
Route for adding multiple tracks to the queue
"""
from quart import redirect, url_for, flash, request, current_app
from ...helpers import login_required
from ...validators.validate_csrf import validate_csrf
from ...validators.validate_add_to_queue import validate_add_multiple

@login_required
async def queue_add_multiple_route(guild_id):
    """
    Handle adding multiple videos to the queue from a playlist
    
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
    
    # Validate form data and extract videos
    is_valid, errors, videos = await validate_add_multiple(form)
    
    # Get parameters that need to be kept even if validation fails
    channel_id = form.get('channel_id')
    playlist_id = form.get('playlist_id')
    page_token = form.get('page_token')
    
    if not is_valid:
        for error in errors:
            flash(error, "error")
            
        # If we have a playlist ID, redirect to the playlist view
        if playlist_id:
            return redirect(url_for('search.youtube_search_route', 
                                  guild_id=guild_id, 
                                  playlist_id=playlist_id))
        else:
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Get user's current voice channel to verify they're in voice
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_state = await discord_client.get_user_voice_state(guild_id, user_id)
    
    # Verify the user is actually in a voice channel
    if not user_voice_state or not user_voice_state.get('channel_id'):
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Check if the bot is connected via the queue info
    queue_info = await discord_client.get_queue(guild_id, channel_id)
    if not queue_info.get('is_connected', False):
        flash("Bot is not connected to your voice channel. Type 'jbot' in a Discord text channel first to connect the bot.", "warning")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Check that user and bot are in the same channel
    if user_voice_state.get('channel_id') != channel_id:
        flash("You must be in the same voice channel as the bot to add music", "warning")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Enforce 50 track limit
    if len(videos) > 50:
        videos = videos[:50]
        flash("Limited to adding 50 videos at once", "warning")
    
    # Add videos to queue
    try:
        result = await discord_client.add_multiple_to_queue(guild_id, channel_id, videos)
        
        if result.get('success'):
            flash(f"Added {result.get('added_count', 0)} videos to queue", "success")
        else:
            flash(f"Error adding videos to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error adding videos to queue: {str(e)}", "error")
    
    # Redirect back to the same playlist page
    if playlist_id:
        return redirect(url_for('search.youtube_search_route', 
                             guild_id=guild_id, 
                             playlist_id=playlist_id, 
                             page_token=page_token))
    else:
        # If somehow we don't have a playlist_id, redirect to the main search
        return redirect(url_for('search.youtube_search_route', guild_id=guild_id))