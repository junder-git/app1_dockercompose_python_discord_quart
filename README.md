# Setup/installation and running mantainance guide  
  
1) Download the whole git repo with git clone or download as zip. (If downloaded as zip maybe extract it to your 'Documents' folder)  
  
2) REPLACE => .env file envs  
  2a ) Go to discord dev portal and sub your application oauth2 secret key and client keys into .env file  
  2b ) Go to youtube data api portal and sub your application key into .env file  
(N.B. if a default env is NONE when provided in param for functions a sub might be made in some places in python files...)    
  
3) INSTALL DOCKER AND DOCKER-COMPOSE  
   (For bot to run and stop succesfully with ```docker-compose``` be sure to navigate to the correct path where you extracted the repository in command prompt i.e.e cmd.exe or powershell, so if you extracted it to C:/User/Documents open command prompt or power shell and:
   ```cd C:/User/Documents/app1_dockercompose_jbot_armv7_discordbot_flaskmanager```)
     
   3a. Now run bot with) ```docker-compose up -d```  
   3b. Or stop bot with) ```docker-compose down -v```  
     
Example dicord "chat model" manager view:  
![Model Image 1](READMEresources/discord_chat_model_example.png)  
  
Example flask webplayer manager view:  
![Webplayer Image 1](READMEresources/flask_webapp_example.png)    
