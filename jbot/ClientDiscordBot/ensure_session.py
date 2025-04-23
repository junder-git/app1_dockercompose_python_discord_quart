"""
Ensure an aiohttp session exists, creating one if needed
"""
import aiohttp

async def ensure_session(session):
    if session is None:
        return aiohttp.ClientSession()
    return session