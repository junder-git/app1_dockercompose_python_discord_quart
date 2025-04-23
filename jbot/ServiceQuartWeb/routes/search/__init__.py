"""
Search Blueprint for Quart Web Service
Handles YouTube search functionality
"""
from quart import Blueprint

# Create blueprint
search_blueprint = Blueprint('search', __name__)

# Import routes
from .youtube_search_route import youtube_search_route

# Register routes with the blueprint
search_blueprint.add_url_rule('/server/<guild_id>/search', 'youtube_search_route', youtube_search_route, methods=['GET'])