"""
Generic method for GET requests
"""
from .ensure_session import ensure_session

async def get_request(base_url, secret_key, session, endpoint, params=None, default_response=None):
    try:
        session = await ensure_session(session)
        headers = {"Authorization": f"Bearer {secret_key}"}
        url = f"{base_url}/{endpoint}"
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                print(f"Error from bot API: {response.status}")
                return default_response or {"success": False, "error": f"API error: {response.status}"}
            return await response.json()
    except Exception as e:
        print(f"Error calling bot API ({endpoint}): {e}")
        return default_response or {"success": False, "error": str(e)}