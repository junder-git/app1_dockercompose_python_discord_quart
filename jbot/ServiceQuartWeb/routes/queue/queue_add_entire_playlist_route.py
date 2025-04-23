"""
Route for adding an entire playlist to the queue
"""
from quart import redirect, url_for, flash, request, current_app
from ...helpers import login_required
from ...validators.validate_csrf import validate_csrf
from ...validators.validate_queue import validate_add_playlist

@login_required
async def queue_add_entire_playlist_route(guild_id):
    """
    Handle adding an entire YouTube playlist to the queue
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        Response: Redirect to appropriate page
    """
    await validate_csrf()
    
    discord = current_app.discord
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get form data
    form = await request.form
    
    # Validate form data
    is_valid, errors = await validate_add_playlist(form)
    
    # Get parameters that need to be kept even if validation fails
    playlist_id = form.get('playlist_id')
    channel_id = form.get('channel_id')
    
    if not is_valid:
        for error in errors:
            flash(error, "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Check 1: Is the user in a voice channel?
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_state = await discord_client.get_user_voice_state(guild_id, user_id)
    
    if not user_voice_state or not user_voice_state.get('channel_id'):
        flash("You must join a voice channel before adding music to the queue", "warning")
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
    
    try:
        # Get playlist videos
        videos, _, total_count = await youtube_client.get_playlist_videos(playlist_id)
        
        if not videos:
            flash("No videos found in playlist", "error")
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
        
        # Enforce 50 track limit
        if len(videos) > 50:
            videos = videos[:50]
            flash(f"Playlist has {total_count} videos, but only the first 50 will be added", "warning")
        
        # Add videos to queue
        result = await discord_client.add_multiple_to_queue(guild_id, channel_id, videos)
        
        if result.get('success'):
            flash(f"Added {result.get('added_count', 0)} videos from playlist to queue", "success")
        else:
            flash(f"Error adding playlist videos: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error processing playlist: {str(e)}", "error")
    
    # After adding the tracks, redirect back to the playlist view
    return redirect(url_for('search.youtube_search_route', 
                         guild_id=guild_id, 
                         playlist_id=playlist_id))