"""
Add entire playlist to queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash, current_app
from .helpers import login_required, get_user_voice_channel
from forms import PlaylistForm

# Create a blueprint for queue add entire playlist route
queue_add_entire_playlist_bp = Blueprint('queue_add_entire_playlist', __name__)

@queue_add_entire_playlist_bp.route('/server/<guild_id>/queue/add_entire_playlist', methods=['POST'])
@login_required
async def queue_add_entire_playlist_route(guild_id):
    """Handle adding an entire YouTube playlist to the queue"""
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    form = await PlaylistForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    playlist_id = form.playlist_id.data
    channel_id = form.channel_id.data
    playlist_title = form.playlist_title.data
    
    videos, _, _ = await youtube_service.get_playlist_videos(playlist_id)
    if not videos:
        flash("No videos found in playlist", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Send the batch add request to the Discord bot
    result = await bot_api.add_multiple_to_queue(guild_id, channel_id, videos)
    
    if result.get('success'):
        flash(f"Added {result.get('added_count', 0)} videos from playlist '{playlist_title}' to queue", "success")
    else:
        flash(f"Error adding videos from playlist: {result.get('error', 'Unknown error')}", "error")
    
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))