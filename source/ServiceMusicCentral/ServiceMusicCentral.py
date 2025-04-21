import sys
import os
from dotenv import load_dotenv
from ClientYoutube import YouTubeService

# First try loading .env.local, then fall back to .env if needed
load_dotenv()
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

"""
start_api_server method for Discord bot
Starts the API server for handling external requests
"""
from aiohttp import web
app = web.Application()
app.add_routes([
            web.get('/api/video_search', self.video_search),
    ])
    
    

# Initialize YouTube service and make it available to routes
app.youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)


if __name__ == "__main__":
    runner = web.AppRunner(app)
    await runner.setup()
    self.api_server = web.TCPSite(runner, '0.0.0.0', 5001)
    await self.api_server.start()
    print("API server started at http://0.0.0.0:5001")