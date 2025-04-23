"""
Dashboard Blueprint for Quart Web Service
Handles the main dashboard for server selection
"""
from quart import Blueprint

# Create blueprint
dashboard_blueprint = Blueprint('dashboard', __name__)

# Import routes
from .dashboard_route import dashboard_route

# Register routes with the blueprint
dashboard_blueprint.add_url_rule("/dashboard", "dashboard_route", dashboard_route)