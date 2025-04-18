"""
Add by URL route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, request, flash
from .helpers import login_required, get_user_voice_channel

# Create a blueprint for add by URL route
add_by_url_bp = Blueprint('add_by_url', __name__)

@add_by_url_bp.route('/server/<guild_id>/add_by_url', methods=['POST'])
@login_required
async def add_by_url_route(guild_id):
    """Handle adding videos by URL - supports both single videos and playlists"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    form = await request.form
    url = form.get('url')
    channel_id = form.get('channel_id')
    
    if not url or not channel_id:
        flash("Missing URL or channel ID", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Use the shared service for URL handling
    is_playlist = youtube_service.extract_playlist_id(url) is not None
    
    try:
        if is_playlist:
            # Extract playlist ID
            playlist_id = youtube_service.extract_playlist_id(url)
            if not playlist_id:
                flash("Invalid YouTube playlist URL", "error")
                return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
            
            # Redirect to playlist confirmation page
            return redirect(url_for('playlist_confirmation.playlist_confirmation_route', 
                                   guild_id=guild_id, 
                                   playlist_id=playlist_id, 
                                   channel_id=channel_id))
        else:
            # Extract video ID
            video_id = youtube_service.extract_video_id(url)
            if not video_id:
                flash("Invalid YouTube video URL", "error")
                return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
            
            # Get video details using the YouTube service
            video_details = await youtube_service.get_video_details(video_id)
            video_title = video_details.get('title', 'Unknown Video')
            
            # Add to queue
            result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
            if result.get('success'):
                flash(f"Added '{video_title}' to queue", "success")
            else:
                flash(f"Error adding video to queue: {result.get('error')}", "error")
        
    except Exception as e:
        flash(f"Error processing URL: {str(e)}", "error")
    
    # Redirect back to dashboard
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))