"""
Public GET method wrapper for route handlers
"""
from .ensure_session import ensure_session

async def public_get(base_url, secret_key, session, endpoint, params=None):
    session = await ensure_session(session)
    headers = {"Authorization": f"Bearer {secret_key}"}

    if '?' in endpoint and params:
        query_string = urlencode(params)
        url = f"{base_url}{endpoint}&{query_string}"
    elif params:
        query_string = urlencode(params)
        url = f"{base_url}{endpoint}?{query_string}"
    else:
        url = f"{base_url}{endpoint}"

    return await session.get(url, headers=headers)