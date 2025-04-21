"""
Clear queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash, current_app
from .helpers import login_required
from forms import ClearQueueForm

# Create a blueprint for queue clear route
queue_clear_bp = Blueprint('queue_clear', __name__)

@queue_clear_bp.route('/server/<guild_id>/queue/clear', methods=['POST'])
@login_required
async def queue_clear_route(guild_id):
    bot_api = current_app.bot_api
    
    form = await ClearQueueForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    try:
        result = await bot_api.clear_queue(guild_id)
        if result.get('success'):
            flash("Music queue cleared", "success")
        else:
            flash(f"Error clearing queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error clearing queue: {str(e)}", "error")
    
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))