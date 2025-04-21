"""
Queue Blueprint for Quart Web Service
Handles queue management operations
"""
from quart import Blueprint, redirect, url_for, flash, request, current_app
from .helpers import login_required, get_user_voice_channel

# Create blueprint
queue_blueprint = Blueprint('queue', __name__)

class AddToQueueForm:
    """Form for adding videos to the queue (used for validation)"""
    pass

class AddMultipleForm:
    """Form for adding multiple videos to the queue (used for validation)"""
    pass

@queue_blueprint.route('/server/<guild_id>/queue/add', methods=['POST'])
@login_required
async def queue_add_route(guild_id):
    """Handle adding videos to the queue"""
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    video_id = form.get('video_id')
    video_title = form.get('video_title', 'Unknown video')
    
    if not all([channel_id, video_id]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Add to queue using the Discord bot API
        result = await discord_client.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result.get('success'):
            flash(f"Added '{video_title}' to queue", "success")
        else:
            flash(f"Error adding to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error adding to queue: {str(e)}", "error")
    
    # Redirect back to the search page or dashboard
    return_to = form.get('return_to', 'server')
    if return_to == 'search':
        return redirect(url_for('search.youtube_search_route', guild_id=guild_id))
    else:
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))

@queue_blueprint.route('/server/<guild_id>/queue/add_multiple', methods=['POST'])
@login_required
async def queue_add_multiple_route(guild_id):
    """Handle adding multiple videos to the queue from a playlist"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Get user's current voice channel to verify they're in voice
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
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
        playlist_id = form.get('playlist_id')
        if playlist_id:
            return redirect(url_for('search.youtube_search_route', guild_id=guild_id, playlist_id=playlist_id))
        else:
            return redirect(url_for('search.youtube_search_route', guild_id=guild_id))
    
    # Add videos to queue
    try:
        result = await discord_client.add_multiple_to_queue(guild_id, channel_id, videos)
        
        if result.get('success'):
            flash(f"Added {result.get('added_count', 0)} videos to queue", "success")
        else:
            flash(f"Error adding videos to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error adding videos to queue: {str(e)}", "error")
    
    # Redirect back to the appropriate page
    playlist_id = form.get('playlist_id')
    if playlist_id:
        page_token = form.get('page_token')
        return redirect(url_for('search.youtube_search_route', 
                              guild_id=guild_id, 
                              playlist_id=playlist_id, 
                              page_token=page_token))
    else:
        return redirect(url_for('search.youtube_search_route', guild_id=guild_id))

@queue_blueprint.route('/server/<guild_id>/queue/add_entire_playlist', methods=['POST'])
@login_required
async def queue_add_entire_playlist_route(guild_id):
    """Handle adding an entire YouTube playlist to the queue"""
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get form data
    form = await request.form
    playlist_id = form.get('playlist_id')
    channel_id = form.get('channel_id')
    
    if not all([playlist_id, channel_id]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Get playlist videos
        videos, _, _ = await youtube_client.get_playlist_videos(playlist_id)
        
        if not videos:
            flash("No videos found in playlist", "error")
            return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
        
        # Add videos to queue
        result = await discord_client.add_multiple_to_queue(guild_id, channel_id, videos)
        
        if result.get('success'):
            flash(f"Added {result.get('added_count', 0)} videos from playlist to queue", "success")
        else:
            flash(f"Error adding playlist videos: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error processing playlist: {str(e)}", "error")
    
    return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))

@queue_blueprint.route('/server/<guild_id>/queue/add_by_url', methods=['POST'])
@login_required
async def add_by_url_route(guild_id):
    """Handle adding videos by URL - supports both single videos and playlists"""
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get form data
    form = await request.form
    url = form.get('url')
    channel_id = form.get('channel_id')
    
    if not all([url, channel_id]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    # Determine if it's a playlist or single video
    is_playlist = youtube_client.extract_playlist_id(url) is not None
    
    try:
        if is_playlist:
            playlist_id = youtube_client.extract_playlist_id(url)
            if not playlist_id:
                flash("Invalid YouTube playlist URL", "error")
                return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
            
            # Redirect to the playlist view to let the user choose videos
            return redirect(url_for('search.youtube_search_route', 
                                   guild_id=guild_id, 
                                   playlist_id=playlist_id, 
                                   channel_id=channel_id))
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
        
    except Exception as e:
        flash(f"Error processing URL: {str(e)}", "error")
    
    return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))