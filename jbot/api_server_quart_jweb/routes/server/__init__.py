"""
Server Blueprint for Quart Web Service
Handles server-specific operations
"""
from quart import Blueprint

# Create blueprint
server_blueprint = Blueprint('server', __name__)

# Import routes
from .bot_join_route import bot_join_route
from .bot_leave_route import bot_leave_route

# Register routes with the blueprint
server_blueprint.add_url_rule('/server/<guild_id>/bot/join', 'bot_join_route', bot_join_route, methods=['POST'])
server_blueprint.add_url_rule('/server/<guild_id>/bot/leave', 'bot_leave_route', bot_leave_route, methods=['POST'])