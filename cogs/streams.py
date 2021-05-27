import discord, urllib.request, json, MySQLdb
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta
from random import randint

WILL_ID = 320246151196704768

with open('./cogs/config.json') as data:
   config = json.load(data)

class Streams(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkCommunityStreams.start()
   
   def cog_unload (self):
      self.checkCommunityStreams.stop()

   @tasks.loop(minutes=5.0)
   async def checkCommunityStreams(self):
      print("\n")
      print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
      print("streams -> loop")
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         for member in self.client.get_all_members():
            liverole = get(member.guild.roles, id=834268646603620403)
            twitchid = 0
            roles = [role.id for role in member.roles]

            if 834268329371631646 in roles:
               cursor.execute(f"SELECT twitchid FROM member_rank WHERE discordid = {member.id} AND twitchid != 0")
               if cursor.rowcount > 0:
                  twitchid = cursor.fetchone()[0]

                  try:
                     url = f'https://api.twitch.tv/helix/streams?user_id={twitchid}'
                     header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
                     request = urllib.request.Request(url, headers=header, method="GET")

                     with urllib.request.urlopen(request) as streamjson:
                        streaminfo = json.loads(streamjson.read().decode())
                  except urllib.error.HTTPError as e:
                     self.client.unload_extension('cogs.streams')
                     if e.code == 401:
                        user = self.client.get_user(WILL_ID)
                        await user.send('Twitch API token has expired. Please visit https://reqbin.com/ to request a new one.\n\nURL is : https://id.twitch.tv/oauth2/token \n\nHeader is: {"client_id": twitch_id, "client_secret": twitch_secret, "grant_type": "client_credentials", "scope": "analytics:read:games channel:read:subscriptions user:read:broadcast"}\n\nWhen this is done, remember to load the cog.')
                     else:
                        print(f'Error: {e.code}')
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

                           
                           request = urllib.request.Request('https://api.twitch.tv/helix/users?id=' + streaminfo['user_id'], headers=header, method="GET")
                           with urllib.request.urlopen(request) as userurl:
                              userinfo = json.loads(userurl.read().decode())
                           userinfo = userinfo['data'][0]
                           description = userinfo['description']
                           icon = userinfo['profile_image_url'] + f'?rand={randint(0, 999999)}'

                           embed=discord.Embed(title=title, url=f"https://www.twitch.tv/{streaminfo['user_login']}", description=description, color=0x55c5c6)
                           embed.set_author(name=streaminfo['user_name'], icon_url=icon)
                           embed.set_thumbnail(url=cover)
                           embed.set_image(url=thumbnail)
                           embed.add_field(name='Game', value=game)
                           await self.client.get_channel(834277711819440148).send(content=f"{member.mention} is live now! Come show your support for our community.", embed=embed)
                           print("streams -> made announcement")

                           await member.add_roles(liverole)
                     else:
                        if 834268646603620403 in roles:
                           await member.remove_roles(liverole)
               else:
                  #await member.send("Please connect your twitch account in the discord so that a live announcement can be made.")
                  pass
      except Exception as e:
         print("checkCommunityStreams")
         print(str(e))

      db.close()
               
def setup (client):
   client.add_cog(Streams(client))