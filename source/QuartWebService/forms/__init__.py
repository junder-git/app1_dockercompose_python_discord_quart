"""
Forms package for JBot Quart application
Each form is defined in its own module
"""

# Import all forms for easy access
from .login_form import LoginForm
from .add_to_queue_form import AddToQueueForm
from .add_multiple_form import AddMultipleForm
from .playlist_form import PlaylistForm
from .music_control_form import MusicControlForm
from .reorder_queue_form import ReorderQueueForm
from .search_form import SearchForm
from .url_form import UrlForm
from .shuffle_queue_form import ShuffleQueueForm
from .clear_queue_form import ClearQueueForm

# List all forms for easy import
__all__ = [
    'LoginForm',
    'AddToQueueForm',
    'AddMultipleForm',
    'PlaylistForm',
    'MusicControlForm',
    'ReorderQueueForm',
    'SearchForm',
    'UrlForm',
    'ShuffleQueueForm',
    'ClearQueueForm'
]