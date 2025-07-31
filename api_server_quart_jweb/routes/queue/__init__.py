"""
Queue Blueprint for Quart Web Service
Handles queue management operations
"""
from quart import Blueprint

# Create blueprint
queue_blueprint = Blueprint('queue', __name__)

# Import routes
from .queue_add_route import queue_add_route
from .queue_add_multiple_route import queue_add_multiple_route
from .queue_add_entire_playlist_route import queue_add_entire_playlist_route
from .add_by_url_route import add_by_url_route
from .queue_reorder_route import queue_reorder_route
from .clear_queue_route import clear_queue_route
from .get_queue_partial import get_queue_partial
from .music_control_route import music_control_route
from .shuffle_queue_route import shuffle_queue_route

# Register routes with the blueprint
queue_blueprint.add_url_rule('/server/<guild_id>/queue/add', 'queue_add_route', queue_add_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue/add_multiple', 'queue_add_multiple_route', queue_add_multiple_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue/add_entire_playlist', 'queue_add_entire_playlist_route', queue_add_entire_playlist_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue/add_by_url', 'add_by_url_route', add_by_url_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue/reorder', 'queue_reorder_route', queue_reorder_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue/clear', 'clear_queue_route', clear_queue_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/queue', 'get_queue_partial', get_queue_partial)
queue_blueprint.add_url_rule('/server/<guild_id>/music/control', 'music_control_route', music_control_route, methods=['POST'])
queue_blueprint.add_url_rule('/server/<guild_id>/music/shuffle', 'shuffle_queue_route', shuffle_queue_route, methods=['POST'])