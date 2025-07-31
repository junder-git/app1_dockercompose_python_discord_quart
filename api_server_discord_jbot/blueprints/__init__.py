"""
Blueprints package for Discord Bot Service - Updated for consolidated structure
"""
from .api import apply as api_blueprint
from .commands import apply as commands_blueprint
from .events import apply as events_blueprint
from .ui import apply as ui_blueprint

__all__ = [
    'api_blueprint',
    'commands_blueprint',
    'events_blueprint',
    'ui_blueprint'
]