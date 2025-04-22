"""
Music Central Service - Main entry point
"""
import os
import sys
import asyncio
from quart import Quart
from hypercorn.config import Config
from hypercorn.asyncio import serve
from dotenv import load_dotenv

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import clients
from clients.youtube_api import YouTubeClient

# Load environment variables
load_dotenv()

# Get configuration from environment
SECRET_KEY = os.environ.get('SECRET_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
API_PORT = int(os.environ.get('MUSIC_CENTRAL_API_PORT', 5002))

# Create the app
app = Quart(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Create YouTube client
app.youtube_client = YouTubeClient(api_key=YOUTUBE_API_KEY)

@app.route('/health')
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.teardown_appcontext
async def shutdown_session(exception=None):
    """Cleanup resources on app shutdown"""
    if hasattr(app, 'youtube_client'):
        app.youtube_client.clear_cache()

if __name__ == '__main__':
    config = Config()
    config.bind = [f"0.0.0.0:{API_PORT}"]
    
    print(f"Starting Music Central Service on port {API_PORT}")
    asyncio.run(serve(app, config))