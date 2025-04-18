"""
Add entire playlist to queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, request, flash
from .helpers import login_required, get_user_voice_channel

# Create a blueprint for queue add entire playlist route
queue_add_entire_playlist_bp = Blueprint('queue_add_entire_playlist', __name__)

@queue_add_entire_playlist_bp.route('/server/<guild_id>/queue/add_entire_playlist', methods=['POST'])
@login_required
async def queue_add_entire_playlist_route(guild_id):
    """Handle adding an entire YouTube playlist to the queue"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    form = await request.form
    playlist_id = form.get('playlist_id')
    channel_id = form.get('channel_id')
    playlist_title = form.get('playlist_title', 'Unknown Playlist')
    
    if not playlist_id or not channel_id:
        flash("Missing playlist ID or channel ID", "error")
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))
    
    # Start by getting the first batch of videos
    added_count = 0
    page_token = None
    total_added = 0
    max_pages = 10  # Limit to 10 pages (500 videos) to prevent abuse
    
    # Process videos in batches
    for _ in range(max_pages):
        videos, next_page_token, _ = await youtube_service.get_playlist_videos(playlist_id, page_token)
        
        if not videos:
            break
            
        # Add each video to the queue
        for video in videos:
            try:
                result = await bot_api.add_to_queue(guild_id, channel_id, video['id'], video['title'])
                if result.get('success'):
                    total_added += 1
            except Exception as e:
                print(f"Error adding video to queue: {e}")
                # Continue with next video
                continue
                
        # If there's no next page, we're done
        if not next_page_token:
            break
            
        # Update page token for next batch
        page_token = next_page_token
    
    if total_added > 0:
        flash(f"Added {total_added} videos from playlist '{playlist_title}' to queue", "success")
    else:
        flash("Failed to add videos from playlist to queue", "error")
    
    # Redirect to dashboard to show the queue
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))