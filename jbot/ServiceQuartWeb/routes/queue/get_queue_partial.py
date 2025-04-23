"""
Get queue partial HTML
"""
from quart import render_template, request
from ...routes.auth import login_required#
from ...services import get_queue_and_bot_state

@login_required
async def get_queue_partial(guild_id):
    """
    Return the queue HTML for the selected channel
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: Rendered queue partial HTML
    """
    channel_id = request.args.get('channel_id')
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, channel_id)

    return await render_template(
        'partials_other/_queue_partial.html',
        queue=queue_info.get("queue", []),
        current_track=queue_info.get("current_track"),
    )