import json, mysql.connector, urllib.request
from discord.ext import commands, tasks
from discord.utils import get

with open('./cogs/config.json') as data:
   config = json.load(data)

class Connection(commands.Cog):

   def __init__ (self, client):
      self.client = client
      #self.checkFollowers.start()

   #def cog_unload (self):
      #self.checkFollowers.stop()

   @commands.Cog.listener()
   async def on_message(self, message):
      if message.channel.id == 829917630579867759 and message.author.id != config['bot_id']:
         unclaimed = True
         username = message.content.replace(" ", "")
         print("\n")
         print("connection -> " + message.author.name + " to " + message.content)

         try:
            url = 'https://api.twitch.tv/helix/users?login=' + username
            header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
            request = urllib.request.Request(url, headers=header, method="GET")

            with urllib.request.urlopen(request) as userjson:
               userinfo = json.loads(userjson.read().decode())
            print(json.dumps(userinfo, indent=3))

         except urllib.error.HTTPError as e:
            if e.code == 401:
               print("connection -> token fail")
               user = self.client.get_user(320246151196704768)
               await user.send('Twitch API token has expired. Please visit https://reqbin.com/ to request a new one.\n\nURL is : https://id.twitch.tv/oauth2/token \n\nHeader is: {"client_id": twitch_id, "client_secret": twitch_secret, "grant_type": "client_credentials", "scope": "analytics:read:games channel:read:subscriptions user:read:broadcast"}\n\nWhen this is done, remember to load the cog.')
            else:
               print(f"connection -> Error: {e.code}")

         else:
            if userinfo['data']:
               db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
               cursor = db.cursor()
               userinfo = userinfo['data'][0]

               try:
                  cursor.execute(f"SELECT twitchid FROM member_rank WHERE discordid = {message.author.id}")
                  twitchid = cursor.fetchone()[0]

                  if cursor.rowcount > 0:
                     print("connection -> found discord row")
                     if twitchid == 0:
                        print("connection -> discord no twitch")
                        cursor.execute(f"SELECT discordname, discordid, points, coins FROM member_rank WHERE twitchid = {userinfo['id']}")
                        member = cursor.fetchone()

                        if cursor.rowcount > 0:
                           print("connection -> found twitch row")
                           discordname = member[0]
                           discordid = member[1]
                           points = member[2]
                           coins = member[3]
                           
                           if discordid == 0:
                              print("connection -> twitch no discord")
                              cursor.execute(f"DELETE FROM member_rank WHERE twitchid = {userinfo['id']}")
                              cursor.execute(f"UPDATE member_rank SET twitchname = '{userinfo['display_name']}', twitchid = {userinfo['id']}, points = points + {points}, coins = coins + {coins} WHERE discordid = {message.author.id}")
                           else:
                              print("connection -> twitch claimed by " + discordname)
                              await message.channel.send(f"This account has already been claimed by {discordname}. If you feel this is a mistake please bring it up to Will.")
                              unclaimed = False
                        else:
                           print("connection -> no twitch row")
                           cursor.execute(f"UPDATE member_rank SET twitchname = '{userinfo['display_name']}', twitchid = {userinfo['id']} WHERE discordid = {message.author.id}")
                  else:
                     print("connection -> no discord row")
                     cursor.execute(f"SELECT twitchid, discordid, discordname FROM member_rank WHERE twitchid = {userinfo['id']}")
                     member = cursor.fetchone()

                     if cursor.rowcount > 0:
                        print("connection -> found twitch row")
                        discordid = member[1]
                        discordname = member[2]

                        if discordid == 0:
                           print("connection -> twitch no discord")
                           cursor.execute(f"UPDATE member_rank SET discordname = '{message.author.name}', discordid = {message.author.id} WHERE twitchid = {userinfo['id']}")
                        else:
                           print("connection -> twitch claimed by " + discordname)
                           await message.channel.send(f"This account has already been claimed by {discordname}. If you feel this is a mistake please bring it up to Will.")
                           unclaimed = False
                     else:
                        print("connection -> no rows at all")
                        print(message.author.name, message.author.id, userinfo['display_name'], userinfo['id'])
                        cursor.execute(f"INSERT INTO member_rank (discordname, discordid, twitchname, twitchid) VALUES ('{message.author.name}', {message.author.id}, '{userinfo['display_name']}', {userinfo['id']})")

                  db.commit()

               except Exception as e:
                  db.rollback()
                  print(str(e))

               else:
                  if unclaimed:
                     try:
                        url = f"https://api.twitch.tv/helix/users/follows?from_id={userinfo['id']}&to_id=158745134"
                        header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
                        request = urllib.request.Request(url, headers=header)

                        with urllib.request.urlopen(request) as followjson:
                           followinfo = json.loads(followjson.read().decode())
                        print(json.dumps(followinfo, indent=3))
                     
                     except urllib.error.HTTPError as e:
                        if e.code == 401:
                           print("connection -> token fail")
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
                        await message.channel.send(f"{message.author.mention} as been connected to {userinfo['display_name']}")
                        print("connection -> " + message.author.name + " connected to " + userinfo['display_name'])
               
               db.close()
            else:
               print("connection -> invalid username " + message.content)
               await message.channel.send(message.content + " is not a valid Twitch username")

async def setup (client):
   print("Connection loaded")
   await client.add_cog(Connection(client))