# JBot - Discord Bot & Quart Website Manager

## Setup & Installation Guide

### Prerequisites
- If not downloading as zip, then youl need Git (for cloning the repository) 
- Must have Docker. Download and install from [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Windows).  
  
### Step 1: Download the Repository

Download the [ZIP file](https://github.com/junder-git/app1_dockercompose_discordbot_quartmanager/archive/refs/heads/main.zip) and extract to your Documents folder.  
  
**Alternative**:
```bash
git clone https://github.com/junder-git/app1_dockercompose_discordbot_quartmanager.git
```  
  
### Step 2: Configure Environment Variables
Locate the `.env.example` file in the extracted directory and rename it `.env` then configure it as follows:  
  
#### Discord API Setup
1. Visit [Discord Developer Portal](https://discord.com/developers)
2. Create a new application
3. Add the redirect url http://localhost/callback to the dev portal    
5. Copy the OAuth2 Secret Key and Client Key to the `.env` file  
6. Invite the bot to the server from discord dev portal with `bot` scope and `admin` permissions in the oauth2 section for guild install.  
  
#### YouTube Data API Setup  
1. Visit [YouTube Data API Portal](https://developers.google.com/youtube/v3)  
2. Create a new application.  
3. Enable the youtube data v3 api for the project.  
4. Create and copy the `API key` to the `.env` file  

**Note**: You can ignore the 'redirect URL' environment variables if you only plan to use the Discord chat interface without the Flask webplayer.

**Important**: Add in the .env your own value for SECRET_KEY    
  
### Step 3: Run the Application
Open Command Prompt (Win+R, type `cmd`) or PowerShell and navigate to the source directory:

```bash
cd C:/<YOUR_WINDOWS_USER_HERE>/Documents/app1_dockercompose_jbot_discordbot_quartmanager/jbot
```

**Start the bot**:
```bash
docker-compose up --build -d
```  
Go to `http://localhost` for the webplayer and/or join a voice chat channel in discord, type `jbot` in any of the servers text channels to get the discord interface to pop up in there. I recommend doing this in a `# bot-channel` or some dedicated text channel.      
  
**Stop the bot**:
```bash
docker-compose down -v
```

## Application Interfaces

### Discord Chat Model Manager
![Discord Chat Interface](READMEresources/discord_chat_model_example.png)

### Flask Webplayer Manager
![Flask Webplayer Interface](READMEresources/flask_webapp_example.png)

## Development Notes

### Security Considerations
- **Current Risk**: Flask API endpoints are publicly accessible
- **Issue**: These endpoints could be used to manipulate queues on other servers without being in the voice channel
- **Solution in Progress**: Implement authentication for Flask endpoints while maintaining necessary accessibility
- **Note**: Discord API is only accessible within the Docker network, so it's protected

![Flask Endpoints](READMEresources/flask_endpoints.png)

### Planned Features
- Twitch bot integration with channel points for song requests
- Track and playlist looping functionality
- Quick access to popular playlists (up to 10 per server)
- Protection against large playlists (100+ tracks)
- Queue size limit of 50 tracks  
- Make sure after clicking add to queue in the flask webplayer search it doesnt clear the search and let it add more to queue  
- Keep the last input in the search query box  
    
### Current Security Features
- Limit of one bot instance per Discord server for any number of voice channels it may have.
  
##### Lind  
-Keep Playlist results until you submit a new search  
-Keep the last input in the search bar  
-Option to loop song or playlist  
-Commmand to add first search result of a qry to the playlist  
-Cache last 2 songs or so?  
-Give option to go back?   