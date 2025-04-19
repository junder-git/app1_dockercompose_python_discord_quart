"""
Add multiple videos to queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required, get_user_voice_channel
from forms import AddMultipleForm

# Create a blueprint for queue add multiple route
queue_add_multiple_bp = Blueprint('queue_add_multiple', __name__)

@queue_add_multiple_bp.route('/server/<guild_id>/queue/add_multiple', methods=['POST'])
@login_required
async def queue_add_multiple_route(guild_id):
    """Handle adding multiple videos to the queue from a playlist"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    
    # Create and validate form
    form = await AddMultipleForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    channel_id = form.channel_id.data
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get all selected video IDs and titles
    video_ids = form.video_ids.data
    video_titles = form.video_titles.data
    
    # Make sure we have data to process
    if not video_ids or len(video_ids) == 0:
        flash("No videos selected", "warning")
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))
    
    # Process each selected video individually to ensure they're added
    added_count = 0
    for i, video_id in enumerate(video_ids):
        # Get the corresponding title if available
        video_title = "Unknown Video"
        if i < len(video_titles):
            video_title = video_titles[i]
        
        try:
            result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
            if result.get('success'):
                added_count += 1
            else:
                flash(f"Error adding '{video_title}' to queue: {result.get('error')}", "error")
        except Exception as e:
            flash(f"Error adding video to queue: {str(e)}", "error")
    
    if added_count > 0:
        flash(f"Added {added_count} videos to queue", "success")
    
    # Go back to the search page or the playlist page if a playlist_id was provided
    playlist_id = form.playlist_id.data
    page_token = form.page_token.data
    if playlist_id:
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id, playlist_id=playlist_id, page_token=page_token))
    else:
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))