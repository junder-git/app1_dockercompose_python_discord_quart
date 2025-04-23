"""
Public POST method wrapper for route handlers
"""
from .ensure_session import ensure_session

async def public_post(base_url, secret_key, session, endpoint, data=None):
    session = await ensure_session(session)
    headers = {"Authorization": f"Bearer {secret_key}"}
    url = f"{base_url}{endpoint}"
    return await session.post(url, headers=headers, json=data)