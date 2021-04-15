import discord, json, MySQLdb, urllib.request, requests
from discord.ext import commands
from discord.utils import get

with open('./cogs/config.json') as data:
   config = json.load(data)

class Connection(commands.Cog):

   def __init__ (self, client):
      self.client = client

   @commands.Cog.listener()
   async def on_message(self, message):
      if message.channel.id == 829917630579867759 and message.author.id != config['bot_id']:
         unclaimed = True
         username = message.content.replace(" ", "")
         print(username, message.author.id, message.author.name)

         try:
            url = 'https://api.twitch.tv/helix/users?login=' + username
            header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
            request = urllib.request.Request(url, headers=header, method="GET")

            with urllib.request.urlopen(request) as userjson:
               userinfo = json.loads(userjson.read().decode())
            print(json.dumps(userinfo, indent=3))

         except urllib.error.HTTPError as e:
            if e.code == 401:
               print("twitch -> token fail")
               user = self.client.get_user(320246151196704768)
               await user.send('Twitch API token has expired. Please visit https://reqbin.com/ to request a new one.\n\nURL is : https://id.twitch.tv/oauth2/token \n\nHeader is: {"client_id": twitch_id, "client_secret": twitch_secret, "grant_type": "client_credentials", "scope": "analytics:read:games channel:read:subscriptions user:read:broadcast"}\n\nWhen this is done, remember to load the cog.')
            else:
               print(f'Error: {e.code}')

         else:
            if userinfo['data']:
               db = MySQLdb.connect("localhost", "root", config['database_pass'], config['database_schema'])
               cursor = db.cursor()

               try:
                  cursor.execute(f"SELECT twitchid, discordid FROM member_rank WHERE twitchid = {userinfo['data'][0]['id']} OR discordid = {message.author.id}")

                  if cursor.rowcount == 0:
                     cursor.execute(f"INSERT INTO member_rank (twitchid, discordid) VALUES ({userinfo['data'][0]['id']}, {message.author.id})")
                  else:
                     memberinfo = cursor.fetchone()
                     if memberinfo[1] is None:
                        cursor.execute(f"UPDATE member_rank SET discordid = {message.author.id} WHERE twitchid = {userinfo['data'][0]['id']}")
                     else:
                        cursor.execute(f"SELECT twitchid FROM member_rank")
                        twitchids = cursor.fetchall()
                        if memberinfo[0] in twitchids:
                           await message.channel.send(f"{userinfo['data'][0]['display_name']} has already been claimed by another user.")
                           unclaimed = False
                        else:
                           cursor.execute(f"UPDATE member_rank SET twitchid = {userinfo['data'][0]['id']} WHERE discordid = {message.author.id}")

                  db.commit()

               except Exception as e:
                  db.rollback()
                  user = self.client.get_user(320246151196704768)
                  await user.send('Error occurred when updating member roles.')
                  print(str(e))

               else:
                  if unclaimed:
                     try:
                        url = f"https://api.twitch.tv/helix/users/follows?from_id={userinfo['data'][0]['id']}&to_id=158745134"
                        header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
                        request = urllib.request.Request(url, headers=header)

                        with urllib.request.urlopen(request) as followjson:
                           followinfo = json.loads(followjson.read().decode())
                        print(json.dumps(followinfo, indent=3))
                     
                     except urllib.error.HTTPError as e:
                        if e.code == 401:
                           print("twitch -> token fail")
                           user = self.client.get_user(320246151196704768)
                           await user.send('Twitch API token has expired. Please visit https://reqbin.com/ to request a new one.\n\nURL is : https://id.twitch.tv/oauth2/token \n\nHeader is: {"client_id": twitch_id, "client_secret": twitch_secret, "grant_type": "client_credentials", "scope": "analytics:read:games channel:read:subscriptions user:read:broadcast"}\n\nWhen this is done, remember to load the cog.')
                        else:
                           print(f'Error: {e.code}')

                     else:
                        if followinfo['data']:
                           role = get(message.guild.roles, id=583864250410336266)
                        else:
                           role = get(message.guild.roles, id=829920585642803250)
                        await message.author.add_roles(role)
                        await message.channel.send(f"{message.author.mention} as been connected to {userinfo['data'][0]['display_name']}")
               
               db.close()
            else:
               await message.channel.send(message.content + " is not a valid Twitch username")

def setup (client):
   client.add_cog(Connection(client))