"""
Clear queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required

# Create a blueprint for queue clear route
queue_clear_bp = Blueprint('queue_clear', __name__)

@queue_clear_bp.route('/server/<guild_id>/queue/clear', methods=['POST'])
@login_required
async def queue_clear_route(guild_id):
    """Explicitly clear the queue for a guild"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    try:
        result = await bot_api.clear_queue(guild_id)
        if result.get('success'):
            flash("Music queue cleared", "success")
        else:
            flash(f"Error clearing queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error clearing queue: {str(e)}", "error")
    
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))