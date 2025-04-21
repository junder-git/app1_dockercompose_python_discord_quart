"""
Music Player Blueprint for Quart
"""
from quart import Blueprint, request, current_app

# Create the blueprint
music_player_blueprint = Blueprint('music_player', __name__, url_prefix='/api/music')

@music_player_blueprint.route('/extract-audio', methods=['GET'])
async def extract_audio_route():
    """Extract audio URL for a YouTube video"""
    music_client = current_app.music_client
    
    video_id = request.args.get('video_id')
    if not video_id:
        return {"error": "Missing video_id parameter"}, 400
    
    audio_url = await music_client.extract_audio_url(video_id)
    if not audio_url:
        return {"error": "Failed to extract audio URL"}, 404
    
    return {"audio_url": audio_url}

@music_player_blueprint.route('/process-url', methods=['POST'])
async def process_url_route():
    """Process a YouTube URL"""
    music_client = current_app.music_client
    
    data = await request.get_json()
    url = data.get('url')
    
    if not url:
        return {"error": "Missing URL parameter"}, 400
    
    result = await music_client.process_youtube_url(url)
    if not result:
        return {"error": "Failed to process URL"}, 404
    
    return result

@music_player_blueprint.route('/search', methods=['GET'])
async def search_route():
    """Search for videos"""
    music_client = current_app.music_client
    
    query = request.args.get('q')
    max_results = int(request.args.get('max_results', 10))
    
    if not query:
        return {"error": "Missing query parameter"}, 400
    
    results = await music_client.search_videos(query, max_results)
    
    return {"results": results}

@music_player_blueprint.route('/ffmpeg-options', methods=['GET'])
async def ffmpeg_options_route():
    """Get FFmpeg options for audio playback"""
    music_client = current_app.music_client
    
    quality = request.args.get('quality', 'medium')
    # Make sure quality is one of the allowed values
    if quality not in ['low', 'medium', 'high']:
        quality = 'medium'
    
    options = music_client.get_ffmpeg_options(quality)
    
    return options