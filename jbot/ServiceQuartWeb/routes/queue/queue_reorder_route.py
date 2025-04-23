"""
Route for reordering tracks in the queue
"""
from quart import redirect, url_for, flash, request, current_app
from ...auth import login_required
from ...validators.validate_csrf import validate_csrf

@login_required
async def queue_reorder_route(guild_id):
    """
    Handle reordering tracks in the queue
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        Response: Redirect to server dashboard
    """
    await validate_csrf()
    
    discord_client = current_app.discord_client
    
    # Get form data
    form = await request.form
    channel_id = form.get('channel_id')
    old_index = form.get('old_index')
    new_index = form.get('new_index')
    
    # Validate input
    if not all([channel_id, old_index is not None, new_index is not None]):
        flash("Missing required information", "error")
        return redirect(url_for('server.server_dashboard_route', guild_id=guild_id))
    
    try:
        # Convert indices to integers
        old_index = int(old_index)
        new_index = int(new_index)
        
        # Reorder the queue using the Discord bot API
        result = await discord_client.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result.get('success'):
            flash(f"Track moved from position {old_index+1} to {new_index+1}", "success")
        else:
            flash(f"Error reordering queue: {result.get('error', 'Unknown error')}", "error")
    except ValueError:
        flash("Invalid index values", "error")
    except Exception as e:
        flash(f"Error reordering queue: {str(e)}", "error")
    
    # Redirect back to the server dashboard
    return redirect(url_for('server.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))