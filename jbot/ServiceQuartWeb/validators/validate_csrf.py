"""
CSRF validation function
"""
from quart import request, abort, current_app

async def validate_csrf():
    """
    Validate CSRF token in the request
    
    Raises:
        400 error if CSRF validation fails
    """
    csrf = current_app.extensions['csrf']
    if not csrf.validate_csrf(request.form.get('csrf_token')):
        abort(400, "CSRF validation failed")