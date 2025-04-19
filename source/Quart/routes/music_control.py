"""
Music control route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required
from forms import MusicControlForm

# Create a blueprint for music control route
music_control_bp = Blueprint('music_control', __name__)

@music_control_bp.route('/server/<guild_id>/music/control', methods=['POST'])
@login_required
async def music_control_route(guild_id):
    """Handle music control commands: join, skip, pause, resume, stop"""
    from quart import current_app
    bot_api = current_app.bot_api
    discord = current_app.discord
    
    form = await MusicControlForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    command = form.command.data
    channel_id = form.channel_id.data
    
    try:
        if command == 'join':
            result = await bot_api.join_voice_channel(guild_id, channel_id)
        elif command == 'skip':
            result = await bot_api.skip_track(guild_id, channel_id)
        elif command == 'pause':
            result = await bot_api.pause_playback(guild_id, channel_id)
        elif command == 'resume':
            result = await bot_api.resume_playback(guild_id, channel_id)
        elif command == 'stop':
            user = await discord.fetch_user()
            user_id = str(user.id)
            result = await bot_api.disconnect_voice_channel(guild_id, user_id, preserve_queue=False)
        else:
            flash(f"Unknown command: {command}", "error")
            return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
        
        if result.get('success'):
            flash(result.get('message', f"{command} command succeeded"), "success")
        else:
            flash(f"Error: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"Error executing command: {str(e)}", "error")
    
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))