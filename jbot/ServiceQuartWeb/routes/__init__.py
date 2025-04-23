"""
Routes package for Quart Web Service
"""
from .auth import auth_blueprint
from .dashboard import dashboard_blueprint
from .search import search_blueprint
from .queue import queue_blueprint

__all__ = [
    'auth_blueprint',
    'dashboard_blueprint',
    'search_blueprint',
    'queue_blueprint'
]

def register_blueprints(app):
    """Register all blueprints with the application"""
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(queue_blueprint)