"""
Routes package for Quart Web Service
"""
from .index import index_blueprint
from .auth import auth_blueprint
from .dashboard import dashboard_blueprint
from .server import server_blueprint
from .search import search_blueprint
from .queue import queue_blueprint

__all__ = [
    'index_blueprint',
    'auth_blueprint',
    'dashboard_blueprint',
    'server_blueprint',
    'search_blueprint',
    'queue_blueprint'
]

def register_blueprints(app):
    """Register all blueprints with the application"""
    app.register_blueprint(index_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(server_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(queue_blueprint)