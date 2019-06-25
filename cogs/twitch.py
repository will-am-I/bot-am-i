import discord
from discord.ext import commands, tasks
import urllib.request, json, requests
from datetime import datetime, timedelta

with open('./cogs/config.json') as data:
   config = json.load(data)

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
      try:
         url = 'https://api.twitch.tv/helix/streams?user_login=will_am_I_'
         header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
         request = urllib.request.Request(url, headers=header)
         print("twitch -> get data")

         with urllib.request.urlopen(request) as streamurl:
            streaminfo = json.loads(streamurl.read().decode())
         print("twitch -> token success")
      except urllib.error.HTTPError as e:
         if e.code == 401:
            print("twitch -> token fail")
            endpoint = 'https://id.twitch.tv/oauth2/token'
            data = {'client_id': config['twitch_id'], 'client_secret': config['twitch_secret'], 'grant_type': 'client_credentials', 'scope': 'analytics:read:games user:read:broadcast'}
            request = requests.post(url=endpoint, data=data)
            token = request['access_token']
            print("twitch -> new token " + token)

            url = 'https://api.twitch.tv/helix/streams?user_login=will_am_I_'
            header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + token}
            request = urllib.request.Request(url, headers=header)
            print("twitch -> get data")

            with urllib.request.urlopen(request) as streamurl:
               streaminfo = json.loads(streamurl.read().decode())
         else:
            print(f'Error: {e.code}')

      print(json.dumps(streaminfo, indent=3))
      if streaminfo['data']:
         streaminfo = streaminfo['data'][0]
         print("twitch -> stream live")

         if datetime.utcnow() - timedelta(minutes=5) <= datetime.strptime(streaminfo['started_at'][:10] + ' ' + streaminfo['started_at'][11:-1], '%Y-%m-%d %H:%M:%S') <= datetime.utcnow():
            print("twitch -> stream live in past 5 minutes")
            gameid = streaminfo['game_id']
            title = streaminfo['title']
            thumbnail = streaminfo['thumbnail_url'].replace('{width}', '640').replace('{height}', '360')

            request = urllib.request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header)
            with urllib.request.urlopen(request) as gameurl:
               gameinfo = json.loads(gameurl.read().decode())
            gameinfo = gameinfo['data'][0]

            game = gameinfo['name']
            cover = gameinfo['box_art_url'].replace('{width}', '272')

            request = urllib.request.Request('https://api.twitch.tv/helix/users?login=will_am_I_', headers=header)
            with urllib.request.urlopen(request) as userurl:
               userinfo = json.loads(userurl.read().decode())
            userinfo = userinfo['data'][0]

            description = userinfo['description']
            icon = userinfo['profile_image_url']

            embed=discord.Embed(title=title, url='https://www.twitch.tv/will_am_I_', description=description, color=0x55c5c6)
            embed.set_author(name='will-am-I', icon_url=icon)
            embed.set_thumbnail(url=cover)
            embed.set_image(url=thumbnail)
            embed.add_field(name='Game', value=game)
            await self.client.get_channel(585925326144667655).send(embed=embed)
            print("twitch -> made announcement")

def setup (client):
   client.add_cog(Twitch(client))