"""
Routes package for JBot Quart application
Each route is defined in its own file as a Blueprint
"""

# Import all route blueprints
from .index import index_bp
from .login import login_bp
from .logout import logout_bp
from .callback import callback_bp
from .dashboard import dashboard_bp
from .server_dashboard import server_dashboard_bp
from .music_control import music_control_bp
from .shuffle_queue import shuffle_queue_bp
from .queue_add import queue_add_bp
from .queue_add_multiple import queue_add_multiple_bp
from .queue_add_entire_playlist import queue_add_entire_playlist_bp
from .queue_clear import queue_clear_bp
from .queue_reorder import queue_reorder_bp
from .queue_ajax import queue_ajax_bp
from .youtube_search import youtube_search_bp
from .add_by_url import add_by_url_bp
from .playlist_confirmation import playlist_confirmation_bp

# List of all blueprints to register
blueprints = [
    index_bp,
    login_bp,
    logout_bp,
    callback_bp,
    dashboard_bp,
    server_dashboard_bp,
    music_control_bp,
    shuffle_queue_bp,
    queue_add_bp,
    queue_add_multiple_bp,
    queue_add_entire_playlist_bp,
    queue_clear_bp,
    queue_reorder_bp,
    queue_ajax_bp,
    youtube_search_bp,
    add_by_url_bp,
    playlist_confirmation_bp
]

def register_blueprints(app):
    """Register all blueprints with the app"""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)