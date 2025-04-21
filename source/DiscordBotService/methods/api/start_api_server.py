"""
start_api_server method for Discord bot
Starts the API server for handling external requests
"""
from aiohttp import web

async def start_api_server(self):
    """
    Start a simple web server to handle API requests from the Quart app
    """
    app = web.Application()
    app.add_routes([
            web.post('/api/join', self.handle_join),
            web.get('/api/guild_count', self.handle_guild_count),
            web.get('/api/guild_ids', self.handle_guild_ids),
            # Queue management routes
            web.post('/api/add_to_queue', self.handle_add_to_queue),
            web.get('/api/get_queue', self.handle_get_queue),
            web.post('/api/skip', self.handle_skip),
            web.post('/api/pause', self.handle_pause),
            web.post('/api/resume', self.handle_resume),
            web.post('/api/disconnect', self.handle_disconnect),
            web.get('/api/get_user_voice_state', self.handle_get_user_voice_state),
            web.post('/api/clear_queue', self.handle_clear_queue),
            web.post('/api/shuffle_queue', self.handle_shuffle_queue),
            web.post('/api/reorder_queue', self.handle_reorder_queue)
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    self.api_server = web.TCPSite(runner, '0.0.0.0', 5001)
    await self.api_server.start()
    print("API server started at http://0.0.0.0:5001")