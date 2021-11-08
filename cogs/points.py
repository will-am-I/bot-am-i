import discord, json, mysql.connector
from datetime import datetime, timedelta
from random import randint
from discord.ext import commands

with open('./cogs/config.json') as data:
   config = json.load(data)

invalid_channels = [585867988016562186, 585925326144667655, 585925326144667655, 653964283104722955, 829939450132955137, 585867244056346646, 829917630579867759, 834261336971673611, 834277711819440148]

class Points(commands.Cog):

   def __init__ (self, client):
      self.client = client

   @commands.Cog.listener()
   async def on_message(self, message):
      if message.channel.id not in invalid_channels and message.author.id != config['bot_id'] and message.author.id != 669228505128501258:
         db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
         cursor = db.cursor()

         try:
            cursor.execute(f"UPDATE member_rank SET points = points + 1 WHERE discordid = {message.author.id}")
            db.commit()

            cursor.execute(f"SELECT DATE_FORMAT(coinlock, '%Y-%m-%d %T') FROM member_rank WHERE discordid = {message.author.id}")
            stamp = cursor.fetchone()[0]
            if datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
               coinlock = (datetime.utcnow() + timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
               cursor.execute(f"UPDATE member_rank SET coins = coins + {randint(1,5)}, coinlock = STR_TO_DATE('{coinlock}', '%Y-%m-%d %T') WHERE discordid = {message.author.id}")
            db.commit()
         except Exception as e:
            db.rollback()
            user = self.client.get_user(320246151196704768)
            await user.send('Error occurred when updating member points.')
            print(str(e))

         db.close()

   @commands.command()
   async def rank(self, ctx):
      pass

   @commands.command()
   async def balance(self, ctx):
      db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute(f"SELECT coins FROM member_rank WHERE discordid = {ctx.message.author.id}")
         credits = cursor.fetchone()[0]
         if cursor.rowcount > 0:
            await ctx.send(f"{ctx.message.author.mention}, you currently have {credits} credits.")
      except Exception as e:
         print(str(e))

      db.close()

def setup (client):
   client.add_cog(Points(client))