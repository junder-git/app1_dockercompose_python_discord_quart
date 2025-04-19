"""
Music control route for JBot Quart application
"""
from quart import Blueprint, request, redirect, url_for, flash
from .helpers import login_required
from forms import MusicControlForm

# Create a blueprint for music control
music_control_bp = Blueprint('music_control', __name__)

@music_control_bp.route('/server/<guild_id>/music-control', methods=['POST'])
@login_required
async def music_control_route(guild_id):
    """Handle music control commands"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    # Get form data
    form = await request.form
    command = form.get('command')
    channel_id = form.get('channel_id')
    
    # Validate inputs
    if not command or not channel_id:
        flash('Invalid command or channel', 'danger')
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Check the bot's current state before issuing command
    state_api_url = f"/api/state/{guild_id}/{channel_id}"
    state_response = await bot_api.get(state_api_url)
    bot_state = {"connected": False, "playing": False, "paused": False}
    
    if state_response.status_code == 200:
        bot_state = await state_response.json()
    
    # Determine if command should be executed based on current state
    execute_command = True
    
    # Skip unnecessary commands based on state
    if command == 'join' and bot_state.get('connected', False):
        execute_command = False
    elif command == 'pause' and (bot_state.get('paused', False) or not bot_state.get('playing', False)):
        execute_command = False
    elif command == 'resume' and (not bot_state.get('paused', False) or not bot_state.get('connected', False)):
        execute_command = False
    elif command == 'skip' and not bot_state.get('playing', False) and not bot_state.get('paused', False):
        execute_command = False
    
    # Execute command if needed
    if execute_command:
        api_url = f"/api/control/{guild_id}/{channel_id}/{command}"
        response = await bot_api.post(api_url)
        
        if response.status_code == 200:
            flash(f'Successfully executed {command}', 'success')
        else:
            error_data = await response.json()
            flash(f'Failed to execute {command}: {error_data.get("error", "Unknown error")}', 'danger')
    else:
        # No need to execute command
        if command == 'join':
            flash('Bot is already connected to the channel', 'info')
        elif command == 'pause':
            flash('Music is already paused or not playing', 'info')
        elif command == 'resume':
            flash('Nothing to resume', 'info')
        elif command == 'skip':
            flash('Nothing to skip', 'info')
    
    # Return to the dashboard
    return_url = request.args.get('return_to', 'server_dashboard.server_dashboard_route')
    return redirect(url_for(return_url, guild_id=guild_id, channel_id=channel_id))