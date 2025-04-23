"""
Close the aiohttp session when done
"""
async def close_session(session):
    if session:
        await session.close()
        return None
    return session