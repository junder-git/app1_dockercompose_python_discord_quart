"""
Blueprints package for Music Central Service
"""
from .audio_blueprint import audio_blueprint
from .search_blueprint import search_blueprint
from .queue_blueprint import queue_blueprint

__all__ = [
    'audio_blueprint',
    'search_blueprint',
    'queue_blueprint'
]