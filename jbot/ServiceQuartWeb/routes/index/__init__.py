"""
Index Blueprint for Quart Web Service
Handles the home page and other static pages
"""
from quart import Blueprint

# Create blueprint
index_blueprint = Blueprint('index', __name__)

# Import routes
from .index_route import index_route

# Register routes with the blueprint
index_blueprint.add_url_rule("/", "index_route", index_route)