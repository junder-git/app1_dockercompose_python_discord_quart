"""
Dashboard Blueprint for Quart Web Service
Handles the main dashboard for server selection
"""
from quart import Blueprint

# Create blueprint
dashboard_blueprint = Blueprint('dashboard', __name__)

# Import routes
from .dashboard_route import dashboard_route
from .index_route import index_route
from .server_dashboard_route import server_dashboard_route

# Register routes with the blueprint
dashboard_blueprint.add_url_rule("/dashboard", "dashboard_route", dashboard_route)
dashboard_blueprint.add_url_rule("/", "index_route", index_route)
dashboard_blueprint.add_url_rule('/server/<guild_id>/dashboard', 'server_dashboard_route', server_dashboard_route)