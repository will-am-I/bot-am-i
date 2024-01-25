import urllib.request, json, mysql.connector
from discord.ext import commands, tasks
from datetime import datetime

with open('./cogs/config.json') as data:
   config = json.load(data)

class Clips(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkClips.start()
   
   def cog_unload (self):
      self.checkClips.cancel()

   @tasks.loop(minutes=2.0)
   async def checkClips (self):
      print("\n")
      print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
      print("clips -> loop")
      url = f"https://api.twitch.tv/helix/clips?broadcaster_id=158745134"
      header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
      request = urllib.request.Request(url, headers=header, method="GET")

      with urllib.request.urlopen(request) as clipsjson:
         clipsinfo = json.loads(clipsjson.read().decode())

      db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute("SELECT clipid FROM twitch_clips")
         results = cursor.fetchall()

         clips = []
         for clip in results:
            clips.append(clip[0])

         for clip in clipsinfo['data']:
            if clip['id'] not in clips:
               print("clips -> found new clip -> " + clip['id'])
               cursor.execute(f"INSERT INTO twitch_clips (clipid) VALUES ('{clip['id']}')")
               await self.client.get_channel(587750670459994112).send(clip['url'])
               print(json.dumps(clip, indent=3))
         
         db.commit()
      except Exception as e:
         db.rollback()
         print("checkClips")
         print(str(e))

      db.close()
               
async def setup (client):
   print("Clips loaded")
   await client.add_cog(Clips(client))