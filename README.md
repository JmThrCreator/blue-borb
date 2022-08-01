# Blue Borb

A discord music bot that you can quickly run and use on your server.

## Functions

Play videos and playlists from YouTube using URLs and titles.
Play mp3 files from the local folder.
Commands: join, leave, play, pause, resume, skip, clear queue, playtop, playskip, shuffle.
Only suitable for use on one server at a time.

## Setup

1. Create a discord bot using the discord developer portal: https://discord.com/developers/docs/intro
2. Copy and paste the token to the file 'token.txt'
3. Set server members intent to true under the Bot setting
4. Give the bot connect and speak permissions under OAuth2
5. Copy the invite link and add the bot to your server

# Linux Setup

```
sudo apt install python3-pip
pip install requirements.txt
sudo apt install ffmpeg
python3 blue_borb.py
```

## Adding to Heroku

1. Clone this git repo and set it up
2. Create Heroku app
3. Install Heroku CLI
5. Add the buildback: https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
4. Run the following:
```
cd [repo location]
heroku login
heroku git:remote -a [app name]
git push heroku master
```
6. Turn on worker python blue_borb.py
