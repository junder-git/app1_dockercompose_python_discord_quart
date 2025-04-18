"""
Add to queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, request, flash
from .helpers import login_required, get_user_voice_channel

# Create a blueprint for queue add route
queue_add_bp = Blueprint('queue_add', __name__)

@queue_add_bp.route('/server/<guild_id>/queue/add', methods=['POST'])
@login_required
async def queue_add_route(guild_id):
    """Handle adding videos to the queue"""
    # Import from current app context 
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    
    # Get the form data asynchronously
    form = await request.form
    
    # Get the requested channel_id from the form
    channel_id = form.get('channel_id')
    video_id = form.get('video_id')
    video_title = form.get('video_title', 'Unknown Video')
    return_to = form.get('return_to', 'dashboard')
    
    if not channel_id or not video_id:
        flash("Missing channel ID or video ID", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # More tolerant check
    user_voice_channel_id = user_voice_channel['id'] if user_voice_channel else None
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel_id:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Try to add the track
    try:
        result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
        if result.get('success'):
            flash(f"Added '{video_title}' to queue", "success")
        else:
            flash(f"Error adding to queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error adding to queue: {str(e)}", "error")
    
    # Redirect back to search results or dashboard with the selected channel
    if return_to == 'search':
        # If coming from search, preserve the search context
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))
    else:
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))