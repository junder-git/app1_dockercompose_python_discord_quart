"""
Reorder queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required
from forms import ReorderQueueForm

# Create a blueprint for queue reorder route
queue_reorder_bp = Blueprint('queue_reorder', __name__)

@queue_reorder_bp.route('/server/<guild_id>/queue/reorder', methods=['POST'])
@login_required
async def queue_reorder_route(guild_id):
    """Handle reordering of tracks in the queue"""
    from quart import current_app
    bot_api = current_app.bot_api
    
    form = await ReorderQueueForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    channel_id = form.channel_id.data
    old_index = int(form.old_index.data)
    new_index = int(form.new_index.data)
    
    try:
        result = await bot_api.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result.get('success'):
            flash("Queue order updated", "success")
        else:
            flash(f"Error reordering queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error reordering queue: {str(e)}", "error")
        
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))