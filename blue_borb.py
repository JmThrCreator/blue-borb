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

# creates global variables
queue = [] 
gloal_ctx = None
paused = False

# COMMANDS

# edit the 'ctx.send' parameters to set custom messages

# On Start
@client.event
async def on_ready():
  print("Blue Borb is ready!")

# Help
@client.command(pass_context=True)
async def help(ctx):
  await ctx.send("Join: ?join\nLeave: ?leave\nPlay: ?play [title/url]\nPlay Local: ?play -local [name]\nSkip: ?skip\nPause: ?pause ?stop\nResume: ?resume\nClear Queue: ?clear\nPlaytop: ?playtop [song]\nPlayskip: ?playskip [song]\nShuffle: ?shuffle")
  
# Join
@client.command(pass_context=True)
async def join(ctx):
  # sets global_ctx to ctx to be used by other functions
  await set_ctx(ctx)

  # unpauses the bot
  global paused
  paused = False

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
      # bot is already in current channel
      if voice_channel.id == client.get_channel("ID"):
        pass
      else:
        await ctx.voice_client.move_to(voice_channel)
  
# Leave
@client.command(pass_context=True)
async def leave(ctx):
  # sets global_ctx to ctx to be used by other functions
  await set_ctx(ctx)

  # unpauses the bot
  global paused
  paused = False

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
  await set_ctx(ctx)

  # if a song is paused, it resumes
  global paused
  if paused:
    paused = False
  
  else:
    # join the voice channel if not already in it
    await join(ctx)


    # plays or queues song
    await play_song(ctx, message, "bot")

# Skip
@client.command(pass_context=True)
async def skip(ctx):
  # sets paused to True
  global paused
  paused = False

  try:
    ctx.voice_client.stop()
    await ctx.send("Skipped")
  except AttributeError:
    await ctx.send("I'm not playing anything")

# Stop
@client.command(pass_context=True)
async def stop(ctx):
  await pause(ctx)

# Pause
@client.command(pass_context=True)
async def pause(ctx):
  global paused

  # the bot is playing
  if ctx.voice_client.is_playing():
    paused = True
    ctx.voice_client.pause()
    await ctx.send("Paused")
  # bot is already paused
  elif paused == True:
    await ctx.send("I'm already paused")
  # bot isn't playing
  else:
    await ctx.send("I'm not playing anything")

# Resume
@client.command(pass_context=True)
async def resume(ctx):
  # sets paused to False
  global paused

  # the bot is playing
  if ctx.voice_client.is_playing():
    await ctx.send("Already playing")
  else:
    paused = False
    ctx.voice_client.resume()
    await ctx.send("Resumed")

# Clear
@client.command(pass_context=True)
async def clear(ctx):
  queue.clear()
  await ctx.send("Queue cleared")

# Playtop
@client.command(pass_context=True)
async def playtop(ctx, *, message):  
  # sets global_ctx to ctx to be used by other functions
  await set_ctx(ctx)

  # unpauses the bot
  global paused
  paused = False

  # checks if the bot is already playing a song
  if not ctx.voice_client.is_playing():
    await ctx.send("I'm not playing anything, you can use ?play")
  else:
    # adds the song to the top of the queue
    queue.insert(0, message)
    
# Playskip
@client.command(pass_context=True)
async def playskip(ctx, *, message):
  # sets global_ctx to ctx to be used by other functions
  await set_ctx(ctx)

  # unpauses the bot
  global paused
  paused = False

  # skips current song if playing
  await skip(ctx)

  # adds song to queue if one is already playing
  await play_song(ctx, message, "bot")

# Shuffle
@client.command(pass_context=True)
async def shuffle(ctx):
  # sets global_ctx to ctx to be used by other functions
  await set_ctx(ctx)

  # shuffles the queue
  global queue
  random.shuffle(queue)

  await ctx.send("Shuffled")

# Show Queue
@client.command(pass_context=True)
async def show_queue(ctx):
  global queue
  
# Only used by the bot

# Play Song
@client.command(pass_context=True)
async def play_song(ctx, message, user):
  global queue
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
    await ctx.send("Song queued")
    queue.append(message)

  # play from local
  elif message[:6] == "-local":
    # seperates the command from the song name
    message = message[7:]
    file_found = False
    foldername = "local"

    # searches folder for the song name
    for file in os.listdir(foldername):
      filename = file.split(".mp3")[0]
      if message == filename:
        file_found = True
        break
    
    # plays the song if the file is found
    if file_found:
      source = discord.FFmpegOpusAudio(source=f"{foldername}/{file}", options = "-loglevel panic")
      vc.play(source)
      await ctx.send(f"Playing {message[6:]}")  
    else:
      await ctx.send(f"Song not found")    
  
  # play from youtube
  else:
    with youtube_dl.YoutubeDL(VDL_OPTIONS) as ydl:
      ydl.cache.remove()

      # checks if the message is a title or url
      extractors = youtube_dl.extractor.gen_extractors()
      message_type = "title"
      for e in extractors:
        if e.suitable(message) and e.IE_NAME != "generic":
          message_type = "url"

      # searches the title and gets the top video url
      if message_type == "title":
        title = message
        info = VideosSearch(title, limit = 1)
        try:
          url = (info.result()["result"][0]["link"])
        except:
          await ctx.send("Invalid title")
          return()
        playlist = False

      # checks if the url is a playlist
      else:
        info = await check_playlist(message)
        url = info[0]
        playlist = info[1]
        playlist_url = info[2]

      # extracts all songs from the playlist and queues them
      if playlist:
        await ctx.send(f"Processing playlist, please wait")
        info = ydl.extract_info(playlist_url, download=False)

        for song in info["entries"]:
          queue.append(song["webpage_url"])

        url2 = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

      # extracts playable url and gets title
      else:
        info = ydl.extract_info(url, download=False)
        url2 = info["formats"][0]["url"]
        title = info.get('title', None)

        # plays song
        source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        vc.play(source)
        await ctx.send(f"Playing {title}")

# Check Playlist
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

# Set CTX
async def set_ctx(ctx):
  # sets global_ctx to ctx to be used by other functions
  global global_ctx
  global_ctx = ctx

# Looped functions

# Queue
async def check_queue():
  while True:
    # checks that a song is in the queue and global_ctx is set
    global global_ctx
    if len(queue) > 0 and global_ctx != None:
      # sets ctx
      ctx = global_ctx

      global paused

      # plays the song if the bot is already playing one and isn't paused
      try:
        if ctx.voice_client.is_playing() == False and paused == False:
          message = queue[0]
          await play_song(ctx, message, "bot")
          queue.pop(0)
      except AttributeError:
        pass
    
    # loops every 1 second
    await asyncio.sleep(1)

# checks the queue
client.loop.create_task(check_queue())

# BOT

# runs the bot
client.run(token)
