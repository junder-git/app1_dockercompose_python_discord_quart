"""
Queue Blueprint for Music Central Service
Handles centralized music queue management
"""
from quart import Blueprint, request, current_app
import os
import json
from collections import defaultdict

# Create a basic in-memory queue storage
# In a production environment, this would be replaced with a persistent storage solution
queues = defaultdict(list)  # guild_id -> list of tracks
current_tracks = {}  # guild_id -> current track
queue_states = {}  # guild_id -> state info (is_playing, is_paused)

# Create blueprint
queue_blueprint = Blueprint('queue', __name__, url_prefix='/api')

@queue_blueprint.route('/queue/<guild_id>', methods=['GET'])
async def get_queue_route(guild_id):
    """Get the queue for a guild"""
    channel_id = request.args.get('channel_id')
    
    # Create a queue ID to ensure proper queue isolation
    queue_id = f"{guild_id}_{channel_id}" if channel_id else guild_id
    
    return {
        "queue": queues.get(queue_id, []),
        "current_track": current_tracks.get(queue_id),
        "state": queue_states.get(queue_id, {"is_playing": False, "is_paused": False})
    }

@queue_blueprint.route('/queue/<guild_id>', methods=['POST'])
async def update_queue_route(guild_id):
    """Update the queue for a guild"""
    data = await request.get_json()
    channel_id = data.get('channel_id')
    queue = data.get('queue', [])
    current_track = data.get('current_track')
    state = data.get('state', {})
    
    # Create a queue ID to ensure proper queue isolation
    queue_id = f"{guild_id}_{channel_id}" if channel_id else guild_id
    
    # Update the queue and state
    queues[queue_id] = queue
    if current_track:
        current_tracks[queue_id] = current_track
    else:
        current_tracks.pop(queue_id, None)
        
    queue_states[queue_id] = state
    
    return {"success": True, "message": "Queue updated"}

@queue_blueprint.route('/queue/<guild_id>/add', methods=['POST'])
async def add_to_queue_route(guild_id):
    """Add a track to the queue"""
    data = await request.get_json()
    channel_id = data.get('channel_id')
    track = data.get('track')
    
    if not track:
        return {"error": "No track provided"}, 400
    
    # Create a queue ID to ensure proper queue isolation
    queue_id = f"{guild_id}_{channel_id}" if channel_id else guild_id
    
    # Add the track to the queue
    queues[queue_id].append(track)
    
    return {
        "success": True,
        "message": f"Added {track.get('title', 'track')} to queue",
        "queue_length": len(queues[queue_id])
    }

@queue_blueprint.route('/queue/<guild_id>/clear', methods=['POST'])
async def clear_queue_route(guild_id):
    """Clear the queue for a guild"""
    data = await request.get_json()
    channel_id = data.get('channel_id')
    
    # If channel ID is provided, only clear that queue
    if channel_id:
        queue_id = f"{guild_id}_{channel_id}"
        queues[queue_id] = []
        current_tracks.pop(queue_id, None)
        queue_states[queue_id] = {"is_playing": False, "is_paused": False}
        return {"success": True, "message": "Queue cleared"}
    
    # Otherwise, clear all queues for this guild
    queues_cleared = 0
    for queue_id in list(queues.keys()):
        if queue_id.startswith(f"{guild_id}_") or queue_id == guild_id:
            queues[queue_id] = []
            current_tracks.pop(queue_id, None)
            queue_states[queue_id] = {"is_playing": False, "is_paused": False}
            queues_cleared += 1
    
    return {"success": True, "message": f"Cleared {queues_cleared} queues"}

@queue_blueprint.route('/queue/<guild_id>/playing', methods=['POST'])
async def update_playing_route(guild_id):
    """Update the currently playing track"""
    data = await request.get_json()
    channel_id = data.get('channel_id')
    track = data.get('track')
    
    # Create a queue ID to ensure proper queue isolation
    queue_id = f"{guild_id}_{channel_id}" if channel_id else guild_id
    
    if track:
        current_tracks[queue_id] = track
        # Auto-set playing state
        if queue_id in queue_states:
            queue_states[queue_id]["is_playing"] = True
            queue_states[queue_id]["is_paused"] = False
        else:
            queue_states[queue_id] = {"is_playing": True, "is_paused": False}
    else:
        current_tracks.pop(queue_id, None)
        # Auto-set playing state
        if queue_id in queue_states:
            queue_states[queue_id]["is_playing"] = False
            queue_states[queue_id]["is_paused"] = False
    
    return {"success": True}

@queue_blueprint.route('/queue/<guild_id>/state', methods=['POST'])
async def update_state_route(guild_id):
    """Update the queue state (playing/paused)"""
    data = await request.get_json()
    channel_id = data.get('channel_id')
    is_playing = data.get('is_playing')
    is_paused = data.get('is_paused')
    
    # Create a queue ID to ensure proper queue isolation
    queue_id = f"{guild_id}_{channel_id}" if channel_id else guild_id
    
    if queue_id not in queue_states:
        queue_states[queue_id] = {"is_playing": False, "is_paused": False}
    
    # Update the state
    if is_playing is not None:
        queue_states[queue_id]["is_playing"] = is_playing
    if is_paused is not None:
        queue_states[queue_id]["is_paused"] = is_paused
    
    return {"success": True}