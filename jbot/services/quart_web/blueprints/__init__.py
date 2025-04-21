"""
Blueprints package for Quart Web Service
"""
from .index_blueprint import index_blueprint
from .auth_blueprint import auth_blueprint
from .dashboard_blueprint import dashboard_blueprint
from .server_blueprint import server_blueprint
from .search_blueprint import search_blueprint
from .queue_blueprint import queue_blueprint

__all__ = [
    'index_blueprint',
    'auth_blueprint',
    'dashboard_blueprint',
    'server_blueprint',
    'search_blueprint',
    'queue_blueprint'
]