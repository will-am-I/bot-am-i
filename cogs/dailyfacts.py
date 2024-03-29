import discord, urllib.request, json
from discord.ext import commands, tasks
from datetime import datetime

with open('./cogs/config.json') as data:
   config = json.load(data)

class DailyFacts(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.getDailyFact.start()
   
   def cog_unload (self):
      self.getDailyFact.cancel()

   @tasks.loop(hours=24)
   async def getDailyFact (self):
      print("\n")
      print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
      print("dailyfacts -> loop")
      try:
         with urllib.request.urlopen("https://uselessfacts.jsph.pl/today.json?language=en") as dailyjson:
            dailyfact = json.loads(dailyjson.read().decode())
         print(f"dailyfacts -> {dailyfact['text']}")

         embed = discord.Embed(title="Did you know?", colour=discord.Colour(0x4e7e8a), description=dailyfact['text'])
         await self.client.get_channel(854921622012297256).send(embed=embed)
      except Exception as e:
         print(str(e))
   
async def setup (client):
   print("DailyFacts loaded")
   await client.add_cog(DailyFacts(client))