# JBot - Discord Bot & Quart Website Manager

A comprehensive Discord music bot with a web interface for management. It includes a Discord bot for music playback in voice channels and a web application for remote control.

## Overview

This application consists of three main services:

1. **Discord Bot Service** - Handles Discord interactions and voice channel functionality
2. **Music Central Service** - Central music processing and queue management
3. **Quart Web Service** - Web interface for controlling the bot from your browser

## Features

- Play music from YouTube in Discord voice channels
- Control music playback via Discord chat commands
- Web interface for remote management
- Search YouTube for videos and playlists
- Queue management (add, remove, reorder, shuffle)
- Multi-server support
- Authentication via Discord OAuth

## Setup & Installation Guide

### Prerequisites

- Docker and Docker Compose
- Discord Bot Token, Client ID, and Client Secret
- YouTube Data API Key

### Step 1: Download the Repository

```bash
git clone https://github.com/yourusername/jbot.git
cd jbot
```

### Step 2: Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:

#### Discord API Setup
1. Visit [Discord Developer Portal](https://discord.com/developers)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token to `DISCORD_BOT_TOKEN` in your `.env` file
5. Go to OAuth2 section and copy the Client ID and Client Secret
6. Add the redirect URL `http://localhost/callback` to OAuth2 Redirects
7. Set the `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, and `DISCORD_REDIRECT_URI` in your `.env` file

#### YouTube Data API Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create API credentials and copy the API key
5. Set the `YOUTUBE_API_KEY` in your `.env` file

#### Security
Generate a secure random string for the `SECRET_KEY` in your `.env` file:

```bash
# Python example for generating a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Invite Bot to Your Server

1. Use the following URL to invite the bot (replace YOUR_CLIENT_ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot
```

2. Select the server you want to add the bot to
3. Authorize the bot with the necessary permissions

### Step 4: Start the Application

Start all services using Docker Compose:

```bash
docker-compose up --build
```

### Step 5: Access the Web Interface

1. Open a web browser and navigate to [http://localhost](http://localhost)
2. Log in with your Discord account
3. Select a server where the bot is present
4. Enjoy managing your music!

## Using the Bot

### Discord Commands

- `jbot` - Show the music control panel in the current channel
- `jbot search <query>` - Search for YouTube videos and add to queue
- `jbot hello` - Test if the bot is responding

### Web Interface

The web interface allows you to:
- Browse your Discord servers
- Manage music queues for each server
- Search YouTube for music
- Add videos and playlists to the queue
- Control playback (play, pause, skip, etc.)

## Architecture

```
+------------------------+     +-----------------------+     +------------------------+
|  Quart Web Service     |     |   Discord Bot Service |     |  Music Central Service |
|  - Web Interface       |     |   - Discord Commands  |     |  - Audio Processing    |
|  - User Authentication |     |   - Voice Connections |     |  - YouTube Integration |
+------------------------+     +-----------------------+     +------------------------+
           |                             |                             |
           |                             |                             |
           v                             v                             v
+------------------------+     +-----------------------+     +------------------------+
|  Discord API Client    |     |   YouTube API Client  |     |  Music Player Client   |
|  - Queue Control       |     |   - Video Search      |     |  - Audio Extraction    |
|  - Playback Management |     |   - Playlist Info     |     |  - Playback Control    |
+------------------------+     +-----------------------+     +------------------------+
```

## Project Structure

```
jbot/
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
├── LICENSE                 # MIT License
├── README.md               # Project documentation
├── docker-compose.yaml     # Docker Compose configuration
│
├── clients/                # Client libraries (shared code)
│   ├── discord_api/        # Discord API client
│   ├── youtube_api/        # YouTube API client
│   └── music_player/       # Music Player client
│
├── services/               # Main service applications
│   ├── discord_bot/        # Discord Bot Service
│   │   ├── Dockerfile      # Discord Bot Dockerfile
│   │   ├── requirements.txt # Discord Bot requirements
│   │   ├── service.py      # Discord Bot entry point
│   │   └── blueprints/     # Discord Bot functionality modules
│   │
│   ├── music_central/      # Music Central Service
│   │   ├── Dockerfile      # Music Central Dockerfile
│   │   ├── requirements.txt # Music Central requirements
│   │   ├── service.py      # Music Central entry point
│   │   └── blueprints/     # Music Central functionality modules
│   │
│   └── quart_web/          # Quart Web Service
│       ├── Dockerfile      # Quart Web Dockerfile
│       ├── requirements.txt # Quart Web requirements
│       ├── service.py      # Quart Web entry point
│       ├── blueprints/     # Quart Web route blueprints
│       ├── static/         # Static assets (CSS, JS)
│       └── templates/      # HTML templates
```

## Development

### Adding New Features

The application is structured using a blueprint pattern for modularity:

1. Discord Bot uses functional blueprints to organize code by feature
2. Quart Web uses the standard Quart blueprint system for routes
3. Music Central uses a similar blueprint approach for API endpoints

To add new features:

1. Identify which service should handle the feature
2. Add necessary methods to the appropriate client library if needed
3. Create or modify blueprints in the relevant service
4. Update templates or commands as needed

### Running in Development Mode

For development, you can use volume mounts to see changes without rebuilding:

```yaml
# In docker-compose.yaml
volumes:
  - ./services/quart_web:/app/quart_web
  - ./clients:/app/clients
```

## Troubleshooting

### Common Issues

1. **Discord Bot not connecting to voice channels**
   - Ensure the bot has proper permissions in your server
   - Check that FFMPEG is properly installed in the container

2. **Web interface authentication failure**
   - Verify your OAuth2 redirect URI is correctly set
   - Check that your client ID and secret are correct

3. **YouTube search not working**
   - Ensure your YouTube API key is valid
   - Check API quota limits on the Google Cloud Console

### Logs

To view logs for debugging:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs discord-bot
docker-compose logs music-central
docker-compose logs quart-web
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Quart](https://github.com/pgjones/quart) - ASGI web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download library