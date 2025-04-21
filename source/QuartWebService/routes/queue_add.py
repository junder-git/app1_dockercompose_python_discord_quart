from quart import Blueprint, redirect, url_for, flash, request, current_app
from .helpers import login_required
from forms import AddToQueueForm

# Create a blueprint for queue add
queue_add_bp = Blueprint('queue_add', __name__)

@queue_add_bp.route('/server/<guild_id>/queue/add', methods=['POST'])
@login_required
async def queue_add_route(guild_id):
    """Handle adding videos to the queue"""
    bot_api = current_app.bot_api
    
    # Create and validate form
    form = await AddToQueueForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get form data
    channel_id = form.channel_id.data
    video_id = form.video_id.data
    video_title = form.video_title.data
    return_to = form.return_to.data
    
    try:
        # Let the Discord bot handle everything - connecting to voice channel and adding to queue
        result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result.get('success'):
            flash(f"Added '{video_title}' to queue", "success")
        else:
            flash(f"Error adding to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error adding to queue: {str(e)}", "error")
    
    # Redirect back based on return_to parameter
    if return_to == 'search':
        return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id))
    else:
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))