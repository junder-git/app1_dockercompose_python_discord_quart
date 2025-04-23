"""
Server Blueprint for Quart Web Service
Handles server-specific dashboard and controls
"""
from quart import Blueprint

# Create blueprint
server_blueprint = Blueprint('server', __name__)

# Import routes
from .server_dashboard_route import server_dashboard_route
from .get_queue_partial import get_queue_partial
from .music_control_route import music_control_route
from .clear_queue_route import clear_queue_route
from .shuffle_queue_route import shuffle_queue_route
from .bot_join_route import bot_join_route
from .bot_leave_route import bot_leave_route

# Register routes with the blueprint
server_blueprint.add_url_rule('/server/<guild_id>/dashboard', 'server_dashboard_route', server_dashboard_route)
server_blueprint.add_url_rule('/server/<guild_id>/queue', 'get_queue_partial', get_queue_partial)
server_blueprint.add_url_rule('/server/<guild_id>/music/control', 'music_control_route', music_control_route, methods=['POST'])
server_blueprint.add_url_rule('/server/<guild_id>/queue/clear', 'clear_queue_route', clear_queue_route, methods=['POST'])
server_blueprint.add_url_rule('/server/<guild_id>/music/shuffle', 'shuffle_queue_route', shuffle_queue_route, methods=['POST'])
server_blueprint.add_url_rule('/server/<guild_id>/bot/join', 'bot_join_route', bot_join_route, methods=['POST'])
server_blueprint.add_url_rule('/server/<guild_id>/bot/leave', 'bot_leave_route', bot_leave_route, methods=['POST'])