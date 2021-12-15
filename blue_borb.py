# IMPORTS
import os
import discord
import youtube_dl
from discord.ext import commands
import asyncio
from youtubesearchpython import VideosSearch
from random import randrange
import random

# TOKEN
file = open("token.txt","r")
token = file.read()
file.close()

# BOT

# sets permissions
intents = discord.Intents.default()
intents.members = True

# creates bot
client = commands.Bot(intents=intents, command_prefix = "?")

# allows you do edit the help command
client.remove_command("help")

# creates global variables (suggestions for a more efficient way to do this welcome)
global queue
global global_ctx
global paused
queue = [] 
global_ctx = []
paused = [False]

# COMMANDS

# search for 'ctx.send' to set custom messages

# Start
@client.event
async def on_ready():
  print("Blue Borb is ready!")

# Join
@client.command(pass_context=True)
async def join(ctx):
  # sets global_ctx to ctx to be used by other functions
  paused.clear()
  paused.append(False)

  # user is not in a voice channel
  if ctx.author.voice is None: 
    await ctx.send("Get in a voice channel fam")

  # user is in a voice channel
  else:
    voice_channel = ctx.author.voice.channel
    # bot is not in a voice channel
    if ctx.voice_client is None: 
      await voice_channel.connect()
    # bot is already in a voice channel
    else: 
      await ctx.voice_client.move_to(voice_channel)
  
# Leave
@client.command(pass_context=True)
async def leave(ctx):
  # sets global_ctx to ctx to be used by other functions
  paused.clear()
  paused.append(False)

  # bot is not in a channel
  if ctx.voice_client is None:
    await ctx.send("I'm not in a channel")
  # user is not in a channel
  elif ctx.author.voice is None:
    await ctx.send("Get in a voice channel fam")
  # bot is in a channel
  else:
    await ctx.voice_client.disconnect()
  
# Play
@client.command(pass_context=True)
async def play(ctx, *, message):
  # sets global_ctx to ctx to be used by other functions
  global_ctx.clear()
  global_ctx.append(ctx)

  # join the voice channel if not already in it
  await join(ctx)

  # queues the song if the bot is already playing one
  if ctx.voice_client.is_playing():
    queue.append(message)

  # plays or queues song
  await play_song(ctx, message, "bot")

# Pause
@client.command(pass_context=True)
async def pause(ctx):
  # sets paused to True
  paused.clear()
  paused.append(True)
  ctx.voice_client.pause()
  await ctx.send("Paused")

# Resume
@client.command(pass_context=True)
async def resume(ctx):
  # sets paused to False
  paused.clear()
  paused.append(False)
  ctx.voice_client.resume()
  await ctx.send("Resumed")

# Clear
@client.command(pass_context=True)
async def clear(ctx):
  queue.clear()

# Playtop
@client.command(pass_context=True)
async def playtop(ctx, *, message):  
  # sets global_ctx to ctx to be used by other functions
  global_ctx.clear()
  global_ctx.append(ctx)

  # checks if the bot is already playing a song
  if not ctx.voice_client.is_playing():
    print("I'm not playing anything, you can use ?play")
  else:
    # adds the song to the top of the queue
    queue.insert(0, message)
    
# Playskip
@client.command(pass_context=True)
async def playskip(ctx, *, message):
  # sets global_ctx to ctx to be used by other functions
  global_ctx.clear()
  global_ctx.append(ctx)

  # checks if a song is playing
  if ctx.voice_client.is_playing():
    ctx.voice_client.stop()
    await ctx.send("Skipped")
  else:
    await ctx.send("Nothing is playing")

  # plays or queues song
  await play_song(ctx, message, "bot")

# Shuffle
@client.command(pass_context=True)
async def shuffle(ctx):
  # sets global_ctx to ctx to be used by other functions
  global_ctx.clear()
  global_ctx.append(ctx)

  # creates a list of the songs in the queue
  temp_queue = []
  for item in queue:
    temp_queue.append(item)

  # shuffles the list
  random.shuffle(temp_queue)

  # sets the queue to the shuffled list
  queue.clear()
  for item in temp_queue:
    queue.append(item)
  await ctx.send("Shuffled")

# Only used by the bot

# Play Song
@client.command(pass_context=True)
async def play_song(ctx, message, user):
  playlist = False
  # makes sure the user isn't using the command
  if user != "bot":
    return()

  # sets options
  FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options":"-vn"}
  VDL_OPTIONS = {"format":"bestaudio"}
  vc = ctx.voice_client

  # if playing, queue
  if vc.is_playing():
    message_list = ["Song queued","Just for you, I will queue this song","Adding it to the queue \n('-)-D[song]               [queue box]"]
    message = message_list[randrange(0, len(message_list))]
    await ctx.send(message)

  # play from local
  elif message[:3] == "-jw":
    file_found = False
    message = message[4:]

    song_identifier = message[0]

    if song_identifier in ("m", "v", "i", "o"):
      message = message[2:]
      for file in os.listdir(f"jw/{song_identifier}"):

        #filepath = r"jw//"
        #filepath = filepath + song_identifier
        #filepath = filepath + r"//"
        #filepath = filepath + file

        filename = file.split(".mp3")[0]
        if message == filename:
          file_found = True
          #media_info = MediaInfo.parse(filepath)
          #for track in media_info.tracks:
          #  if track.track_type == 'General':
          #    print(track.title)    
          break
        
    if file_found == True:
      source = discord.FFmpegOpusAudio(source=f"jw/{song_identifier}/{file}", options = "-loglevel panic")
      vc.play(source)
      await ctx.send(f"Playing {message[3:]}")  
    else:
      await ctx.send(f"Song not found")    

  #play from youtube
  else:
    with youtube_dl.YoutubeDL(VDL_OPTIONS) as ydl:
      ydl.cache.remove()

      #title or url?
      extractors = youtube_dl.extractor.gen_extractors()
      message_type = "title"
      for e in extractors:
        if e.suitable(message) and e.IE_NAME != "generic":
          message_type = "url"

      #if title:
      if message_type == "title":
        title = message
        info = VideosSearch(title, limit = 1)
        try:
          url = (info.result()["result"][0]["link"])
        except:
          print("invalid title")
          return()
        playlist = False

      #if url:
      else:
        info = await check_playlist(message)
        url = info[0]
        playlist = info[1]
        playlist_url = info[2]
      
      #if url is a playlist:
      if playlist == True:
        print(playlist_url)
        await ctx.send(f"Processing playlist, please wait")
        info = ydl.extract_info(playlist_url, download=False)
        count = 0
        while True:
          try:
            if count > 0:
              queue.append(info["entries"][count]["webpage_url"])
          except:
            break
          count+= 1

        url2 = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

      #if not a playlist
      else:
        print(url)
        info = ydl.extract_info(url, download=False)
        url2 = info["formats"][0]["url"]
        title = info.get('title', None)

      #play audio
      source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
      
      vc.play(source)
      
      await ctx.send(f"Playing {title}")

#Queue
async def check_queue():
  while True:
    # checks that a song is in the queue and global_ctx is set
    if len(queue) > 0 and len(global_ctx) > 0:
      # sets ctx
      ctx = global_ctx[0]

      # plays the song if the bot is already playing one and isn't paused
      if not ctx.voice_client.is_playing() and paused[0] == False:
        message = queue[0]
        await play_song(ctx, message, "bot")
        queue[0]
    
    #loops every 1 second
    await asyncio.sleep(1)

#Check Playlist
async def check_playlist(url):
  # if the url is a video in a playlist, it returns the video only
  if "&list=" in url:
    playlist_url = url
    url = url.split("&list=")[0]
    playlist = False
  # if the url is a playlist, it returns the playlist
  elif "?list=" in url:
    playlist_url = url
    url = url.split("?list=")[0]
    playlist = True
  else:
    playlist = False
    playlist_url = None
  return(url, playlist, playlist_url)

# checks the queue
client.loop.create_task(check_queue())

# BOT

# runs the bot
client.run(token)