"""
Add by URL route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required, get_user_voice_channel
from forms import UrlForm

# Create a blueprint for add by URL route
add_by_url_bp = Blueprint('add_by_url', __name__)

@add_by_url_bp.route('/server/<guild_id>/add_by_url', methods=['POST'])
@login_required
async def add_by_url_route(guild_id):
    """Handle adding videos by URL - supports both single videos and playlists"""
    from quart import current_app
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    form = await UrlForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    url = form.url.data
    channel_id = form.channel_id.data
    
    # Determine if it's a playlist or single video
    is_playlist = youtube_service.extract_playlist_id(url) is not None
    
    try:
        if is_playlist:
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
            
            # Let the Discord bot handle the connection and queueing
            result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
            if result.get('success'):
                flash(f"Added '{video_title}' to queue", "success")
            else:
                flash(f"Error: {result.get('error', 'Unknown error')}", "error")
        
    except Exception as e:
        flash(f"Error processing URL: {str(e)}", "error")
    
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))