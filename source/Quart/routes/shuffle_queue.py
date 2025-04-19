"""
Shuffle queue route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required
from forms import ShuffleQueueForm

# Create a blueprint for shuffle queue route
shuffle_queue_bp = Blueprint('shuffle_queue', __name__)

@shuffle_queue_bp.route('/server/<guild_id>/music/shuffle', methods=['POST'])
@login_required
async def shuffle_queue_route(guild_id):
    """Shuffle the current music queue"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    # Create and validate form
    form = await ShuffleQueueForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    channel_id = form.channel_id.data
    
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