# JBot - Discord Bot & Flask Manager

## Setup & Installation Guide

### Prerequisites
- Git (for cloning the repository)
- Docker and Docker Compose

### Step 1: Download the Repository
```bash
git clone https://github.com/junder-git/app1_dockercompose_armv7_discordbot_flaskmanager.git
```
**Alternative**: Download the [ZIP file](https://github.com/junder-git/app1_dockercompose_armv7_discordbot_flaskmanager/archive/refs/heads/main.zip) and extract to your Documents folder.

### Step 2: Configure Environment Variables
Locate the `.env` file in the extracted directory and configure:

#### Discord API Setup
1. Visit [Discord Developer Portal](https://discord.com/developers)
2. Create a new application
3. Copy the OAuth2 Secret Key and Client Key to the `.env` file

#### YouTube Data API Setup
1. Visit [YouTube Data API Portal](https://developers.google.com/youtube/v3)
2. Create a new application
3. Copy the API key to the `.env` file

**Note**: You can ignore the 'redirect URL' environment variables if you only plan to use the Discord chat interface without the Flask webplayer.

**Important**: If a parameter has a default value of "NONE" in Python files, a substitution might occur in some cases.

### Step 3: Install Docker and Docker Compose
Download and install from [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Windows).

### Step 4: Run the Application
Open Command Prompt (Win+R, type `cmd`) or PowerShell and navigate to the source directory:

```bash
cd C:/User/Documents/app1_dockercompose_jbot_armv7_discordbot_flaskmanager/source
```

**Start the bot**:
```bash
docker-compose up -d
```

**Stop the bot**:
```bash
docker-compose down -v
```

## Application Interfaces

### Discord Chat Model Manager
![Discord Chat Interface](source/READMEresources/discord_chat_model_example.png)

### Flask Webplayer Manager
![Flask Webplayer Interface](source/READMEresources/flask_webapp_example.png)

## Development Notes

### Security Considerations
- **Current Risk**: Flask API endpoints are publicly accessible
- **Issue**: These endpoints could be used to manipulate queues on other servers without being in the voice channel
- **Solution in Progress**: Implement authentication for Flask endpoints while maintaining necessary accessibility
- **Note**: Discord API is only accessible within the Docker network, so it's protected

![Flask Endpoints](source/READMEresources/flask_endpoints.png)

### Planned Features
- Twitch bot integration with channel points for song requests
- Track and playlist looping functionality
- Quick access to popular playlists (up to 10 per server)
- Protection against large playlists (100+ tracks)
- Queue size limit of 50 tracks
- Limit of one bot instance per Discord server
