"""
Reorder queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, request, flash
from .helpers import login_required

# Create a blueprint for queue reorder route
queue_reorder_bp = Blueprint('queue_reorder', __name__)

@queue_reorder_bp.route('/server/<guild_id>/queue/reorder', methods=['POST'])
@login_required
async def queue_reorder_route(guild_id):
    """Handle reordering of tracks in the queue"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    form = await request.form
    channel_id = form.get('channel_id')
    old_index = form.get('old_index')
    new_index = form.get('new_index')
    
    if not all([channel_id, old_index, new_index]):
        flash("Missing parameters for queue reordering", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Convert to integers
        old_index = int(old_index)
        new_index = int(new_index)
        
        # Call the API to reorder the queue
        result = await bot_api.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result.get('success'):
            flash("Queue order updated", "success")
        else:
            flash(f"Error reordering queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error reordering queue: {str(e)}", "error")
        
    # Redirect back to the dashboard
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))