"""
Shuffle queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, request, flash
from .helpers import login_required

# Create a blueprint for shuffle queue route
shuffle_queue_bp = Blueprint('shuffle_queue', __name__)

@shuffle_queue_bp.route('/server/<guild_id>/music/shuffle', methods=['POST'])
@login_required
async def shuffle_queue_route(guild_id):
    """Shuffle the current music queue"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    channel_id = request.args.get('channel_id')
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Call the bot API to shuffle the queue
        result = await bot_api.shuffle_queue(guild_id, channel_id)
        if result.get('success'):
            flash("Music queue shuffled", "success")
        else:
            flash(f"Error shuffling queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error shuffling queue: {str(e)}", "error")
    
    # Redirect back to dashboard with the selected channel
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))