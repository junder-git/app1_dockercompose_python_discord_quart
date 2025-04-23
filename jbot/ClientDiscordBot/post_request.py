"""
Generic method for POST requests
"""
from .ensure_session import ensure_session

async def post_request(base_url, secret_key, session, endpoint, data):
    try:
        session = await ensure_session(session)
        headers = {"Authorization": f"Bearer {secret_key}"}
        url = f"{base_url}/{endpoint}"
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                print(f"Error from bot API: {response.status}")
                return {"success": False, "error": f"API error: {response.status}"}
            return await response.json()
    except Exception as e:
        print(f"Error calling bot API ({endpoint}): {e}")
        return {"success": False, "error": str(e)}