"""
Login required decorator for route protection
"""
from functools import wraps
from quart import redirect, url_for, session, current_app

def login_required(f):
    """
    Decorator to protect routes that require authentication
    
    Args:
        f: The function to wrap
        
    Returns:
        The wrapped function that checks for login
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        print(f"Login check - Session contains: {list(session.keys())}")
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for('auth.login_route'))
        print(f"User {session.get('username')} authenticated, proceeding to route")
        return await f(*args, **kwargs)
    return decorated_function