"""
Queue Blueprint for Quart Web Service
Handles queue management operations
"""
from quart import Blueprint, redirect, url_for, flash, request, current_app
from .helpers import login_required

# Create blueprint
queue_blueprint = Blueprint('queue', __name__)

@queue_blueprint.route('/server/<guild_id>/queue/add', methods=['POST'])
@login_required
async def queue_add_route(guild_id):
    """Handle adding videos to the queue"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    video_id = form.get('video_id')
    video_title = form.get('video_title', 'Unknown video')
    
    # Capture search query parameters to preserve them
    query = form.get('query')
    search_type = form.get('search_type', 'comprehensive')
    playlist_id = form.get('playlist_id')
    page_token = form.get('page_token')
    
    if not all([channel_id, video_id]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
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

@queue_blueprint.route('/server/<guild_id>/queue/add_multiple', methods=['POST'])
@login_required
async def queue_add_multiple_route(guild_id):
    """Handle adding multiple videos to the queue from a playlist"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    playlist_id = form.get('playlist_id')
    page_token = form.get('page_token')
    
    if not channel_id:
        flash("Missing channel ID", "error")
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
    
    # Process videos
    videos = []
    video_ids = []
    video_titles = []
    
    # Get all video IDs and titles from form data
    for key, value in form.items():
        if key.startswith('video_ids-'):
            video_ids.append(value)
        elif key.startswith('video_titles-'):
            video_titles.append(value)
    
    # Create videos list
    for i, video_id in enumerate(video_ids):
        title = "Unknown Video"
        if i < len(video_titles):
            title = video_titles[i]
        
        videos.append({
            'id': video_id,
            'title': title
        })
    
    if not videos:
        flash("No videos selected", "warning")
        # Redirect based on whether we were in a playlist view
        if playlist_id:
            return redirect(url_for('search.youtube_search_route', guild_id=guild_id, playlist_id=playlist_id))
        else:
            return redirect(url_for('search.youtube_search_route', guild_id=guild_id))
    
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

@queue_blueprint.route('/server/<guild_id>/queue/add_entire_playlist', methods=['POST'])
@login_required
async def queue_add_entire_playlist_route(guild_id):
    """Handle adding an entire YouTube playlist to the queue"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get form data
    form = await request.form
    playlist_id = form.get('playlist_id')
    channel_id = form.get('channel_id')
    
    if not all([playlist_id, channel_id]):
        flash("Missing required information", "error")
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

@queue_blueprint.route('/server/<guild_id>/queue/add_by_url', methods=['POST'])
@login_required
async def add_by_url_route(guild_id):
    """Handle adding videos by URL - supports both single videos and playlists"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get form data
    form = await request.form
    url = form.get('url')
    channel_id = form.get('channel_id')
    
    if not all([url, channel_id]):
        flash("Missing required information", "error")
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
    
    # Determine if it's a playlist or single video
    is_playlist = youtube_client.extract_playlist_id(url) is not None
    
    try:
        if is_playlist:
            playlist_id = youtube_client.extract_playlist_id(url)
            if not playlist_id:
                flash("Invalid YouTube playlist URL", "error")
                return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
            
            # Fetch the videos from the playlist
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
                
            # Redirect to the playlist view
            return redirect(url_for('search.youtube_search_route', 
                                  guild_id=guild_id, 
                                  playlist_id=playlist_id))
                
        else:
            # Extract video ID
            video_id = youtube_client.extract_video_id(url)
            if not video_id:
                flash("Invalid YouTube video URL", "error")
                return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
            
            # Get video details using the YouTube service
            video_details = await youtube_client.get_video_details(video_id)
            video_title = video_details.get('title', 'Unknown Video')
            
            # Add to queue
            result = await discord_client.add_to_queue(guild_id, channel_id, video_id, video_title)
            
            if result.get('success'):
                flash(f"Added '{video_title}' to queue", "success")
            else:
                flash(f"Error adding to queue: {result.get('error', 'Unknown error')}", "error")
            
            # Redirect back to search with the URL as query
            return redirect(url_for('search.youtube_search_route', 
                                  guild_id=guild_id, 
                                  query=url))
        
    except Exception as e:
        flash(f"Error processing URL: {str(e)}", "error")
    
    # Fallback redirect if something goes wrong
    return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))

@queue_blueprint.route('/server/<guild_id>/queue/reorder', methods=['POST'])
@login_required
async def queue_reorder_route(guild_id):
    """Handle reordering tracks in the queue"""
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    old_index = form.get('old_index')
    new_index = form.get('new_index')
    
    if not all([channel_id, old_index is not None, new_index is not None]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Convert indices to integers
        old_index = int(old_index)
        new_index = int(new_index)
        
        # Reorder the queue using the Discord bot API
        result = await discord_client.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result.get('success'):
            flash(f"Track moved from position {old_index+1} to {new_index+1}", "success")
        else:
            flash(f"Error reordering queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error reordering queue: {str(e)}", "error")
    
    # Redirect back to the server dashboard
    return redirect(url_for('server.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))