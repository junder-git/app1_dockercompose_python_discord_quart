"""
Blueprints package for Discord Bot Service
"""
from .api_blueprint import apply as api_blueprint
from .commands_blueprint import apply as commands_blueprint
from .events_blueprint import apply as events_blueprint
from .queue_blueprint import apply as queue_blueprint
from .playback_blueprint import apply as playback_blueprint
from .voice_blueprint import apply as voice_blueprint
from .ui_blueprint import apply as ui_blueprint

__all__ = [
    'api_blueprint',
    'commands_blueprint',
    'events_blueprint',
    'queue_blueprint',
    'playback_blueprint',
    'voice_blueprint',
    'ui_blueprint'
]