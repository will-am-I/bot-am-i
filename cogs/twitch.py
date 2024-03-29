import discord, urllib.request, json
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta
from random import randint

WILL_ID = 320246151196704768

with open('./cogs/config.json') as data:
   config = json.load(data)

class Twitch(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkStream.start()
   
   def cog_unload (self):
      self.checkStream.cancel()

   @tasks.loop(minutes=5.0)
   async def checkStream (self):
      print("\n")
      print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
      print("twitch -> loop")
      try:
         url = 'https://api.twitch.tv/helix/streams?user_login=will_am_I_'
         header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
         request = urllib.request.Request(url, headers=header, method="GET")

         with urllib.request.urlopen(request) as streamurl:
            streaminfo = json.loads(streamurl.read().decode())

      except urllib.error.HTTPError as e:
         if e.code == 401:
            user = self.client.get_user(WILL_ID)
            await user.send('Twitch API token has expired. Please visit https://reqbin.com/ to request a new one.\n\nURL is : https://id.twitch.tv/oauth2/token \n\nHeader is: {"client_id": twitch_id, "client_secret": twitch_secret, "grant_type": "client_credentials", "scope": scope}\n\nWhen this is done, remember to load the cog.')
         else:
            print(f'Error: {e.code}')
         await self.client.unload_extension('cogs.twitch')
      else:
         if streaminfo['data']:
            streaminfo = streaminfo['data'][0]
            print("twitch -> stream live")
            print(json.dumps(streaminfo, indent=3))

            if datetime.utcnow() - timedelta(seconds=330) <= datetime.strptime(streaminfo['started_at'][:10] + ' ' + streaminfo['started_at'][11:-1], '%Y-%m-%d %H:%M:%S') <= datetime.utcnow():
               gameid = streaminfo['game_id']
               title = streaminfo['title']
               thumbnail = streaminfo['thumbnail_url'].replace('{width}', '640').replace('{height}', '360') + f'?rand={randint(0, 999999)}'

               request = urllib.request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header, method="GET")
               with urllib.request.urlopen(request) as gameurl:
                  gameinfo = json.loads(gameurl.read().decode())
               gameinfo = gameinfo['data'][0]
               game = gameinfo['name']
               cover = gameinfo['box_art_url'].replace('{width}', '272').replace('{height}', '380').replace('/./', '/') + f'?rand={randint(0, 999999)}'

               request = urllib.request.Request('https://api.twitch.tv/helix/users?login=will_am_i_', headers=header, method="GET")
               with urllib.request.urlopen(request) as userurl:
                  userinfo = json.loads(userurl.read().decode())
               userinfo = userinfo['data'][0]
               description = userinfo['description']
               icon = userinfo['profile_image_url'] + f'?rand={randint(0, 999999)}'

               embed=discord.Embed(title=title, url='https://www.twitch.tv/will_am_I_', description=description, color=0x55c5c6)
               embed.set_author(name='will-am-I', icon_url=icon)
               embed.set_thumbnail(url=cover)
               embed.set_image(url=thumbnail)
               embed.add_field(name='Game', value=game)
               await self.client.get_channel(585925326144667655).send(content='<@&583864250410336266>, your favorite speedrunner is now live! Come hang out!', embed=embed)
               print("twitch -> made announcement")

async def setup (client):
   print("Twitch loaded")
   await client.add_cog(Twitch(client))