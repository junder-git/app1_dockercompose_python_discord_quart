"""
Clear queue route
"""
from quart import redirect, url_for, current_app
from ...routes.auth import login_required

@login_required
async def clear_queue_route(guild_id):
    """
    Handle clearing the queue
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: Redirect to server dashboard
    """
    discord_client = current_app.discord_client
    
    # Simply clear all queues for this guild
    await discord_client.clear_queue(guild_id)
    
    # Return to the dashboard
    return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))