import discord, urllib.request, json, requests
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from twitch import TwitchHelix
from random import randint

with open('./cogs/config.json') as data:
   config = json.load(data)

twitch_client = TwitchHelix(client_id=config['twitch_id'], oauth_token=config['twitch_token'])

class Twitch(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkStream.start()
   
   def cog_unload (self):
      self.checkStream.stop()

   #Twitch Live Check (Every 5 Minutes)
   @tasks.loop(minutes=5.0)
   async def checkStream (self):
      print("twitch -> loop")
      print(datetime.now())
      
      stream = twitch_client.get_streams(user_logins='will_am_i_')
      if stream:
         stream = stream[0]
         print("twitch -> stream live")

         if datetime.utcnow() - timedelta(minutes=5) <= stream['started_at'] <= datetime.utcnow():
            print("twitch -> stream live in past 5 minutes")
            gameid = stream['game_id']
            title = stream['title']
            thumbnail = stream['thumbnail_url'].replace('{width}', '640').replace('{height}', '360') + f'?rand={randint(0, 999999)}'

            gameinfo = twitch_client.get_games(game_ids=gameid)
            gameinfo = gameinfo[0]
            game = gameinfo['name']
            cover = gameinfo['box_art_url'].replace('{width}', '272').replace('{height}', '380') + f'?rand={randint(0, 999999)}'

            header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
            request = urllib.request.Request('https://api.twitch.tv/helix/users?login=will_am_i_', headers=header)
            with urllib.request.urlopen(request) as userurl:
               userinfo = json.loads(userurl.read().decode())
            userinfo = userinfo['data'][0]
            description = userinfo['description']
            icon = userinfo['profile_image_url']

            embed=discord.Embed(title=title, url='https://www.twitch.tv/will_am_I_', description=description, color=0x55c5c6)
            embed.set_author(name='will-am-I', icon_url=icon)
            embed.set_thumbnail(url=cover)
            print("twitch -> embed -> thumbnail -> " + cover)
            embed.set_image(url=thumbnail)
            embed.add_field(name='Game', value=game)
            await self.client.get_channel(585925326144667655).send(content="<@&583864250410336266>, Will is now", embed=embed)
            print("twitch -> made announcement")

def setup (client):
   client.add_cog(Twitch(client))