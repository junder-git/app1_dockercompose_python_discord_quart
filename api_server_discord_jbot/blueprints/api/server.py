"""
API Server setup for Discord Bot
"""
from aiohttp import web
from .handlers import get_api_handlers

async def setup_hook(self):
    """Called when the bot starts up"""
    print("Setup hook called!")
    
    # Start the API server
    await self.start_api_server()
    print("API server started")
    
    # Load slash commands if they were registered
    if hasattr(self, '_slash_commands_setup'):
        try:
            await self._slash_commands_setup(self)
            print("Slash commands loaded successfully")
        except Exception as e:
            print(f"Error loading slash commands: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No slash commands setup function found")
    
    # List all commands in tree
    print(f"Commands in tree: {len(self.tree.get_commands())}")
    for cmd in self.tree.get_commands():
        print(f"  - Command: {cmd.name} | Description: {cmd.description}")
    
    # Don't sync here - wait for on_ready when guilds are available
    print("Waiting for bot to be ready to sync commands to guilds...")

async def start_api_server(self):
    """
    Start a web server to handle API requests from the Quart app
    """
    app = web.Application()
    app.add_routes([
        # Guild information
        web.get('/api/guild_count', self.handle_guild_count),
        web.get('/api/guild_ids', self.handle_guild_ids),
        
        # Queue management
        web.post('/api/add_to_queue', self.handle_add_to_queue),
        web.get('/api/get_queue', self.handle_get_queue),
        web.post('/api/clear_queue', self.handle_clear_queue),
        web.post('/api/shuffle_queue', self.handle_shuffle_queue),
        web.post('/api/reorder_queue', self.handle_reorder_queue),
        
        # Playback control
        web.post('/api/skip', self.handle_skip),
        web.post('/api/pause', self.handle_pause),
        web.post('/api/resume', self.handle_resume),
        
        # Voice connection
        web.post('/api/join', self.handle_join),
        web.post('/api/disconnect', self.handle_disconnect),
        
        # User information
        web.get('/api/get_user_voice_state', self.handle_get_user_voice_state),
    ])
    
    # Get API port from environment or use default
    api_port = 5001
    
    runner = web.AppRunner(app)
    await runner.setup()
    self.api_server = web.TCPSite(runner, '0.0.0.0', api_port)
    await self.api_server.start()
    print(f"API server started at http://0.0.0.0:{api_port}")