"""
Shuffle queue route
"""
from quart import redirect, url_for, current_app, flash, request
from ...routes.auth.login_required import login_required

@login_required
async def shuffle_queue_route(guild_id):
    """
    Handle shuffling the queue
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: Redirect to server dashboard
    """
    form = await request.form
    channel_id = form.get('channel_id')
    
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Shuffle the queue
    result = await current_app.discord_api_client.shuffle_queue(guild_id, channel_id)
    
    if result.get('success'):
        flash("Queue shuffled successfully", "success")
    else:
        flash(f"Error shuffling queue: {result.get('error', 'Unknown error')}", "error")
    
    # Redirect back to the server dashboard
    return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))