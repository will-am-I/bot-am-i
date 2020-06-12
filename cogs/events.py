import discord
from discord.ext import commands

class Events(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   #Ready
   @commands.Cog.listener()
   async def on_ready(self):
      await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="just a bot boy from a bot family" ))
      print('bot-am-i is here')
   
   #Member join
   @commands.Cog.listener()
   async def on_member_join(self, member):
      embed=discord.Embed(title="Welcome to the ThumbWars!", description=f"Everyone say hello to **{member.name}**", color=0x55c5c6)
      embed.set_thumbnail(url=member.avatar_url)
      await self.client.get_channel(585867244056346646).send(embed=embed)
      print(f'{member} has joined the server.')
      
   #Member leave
   @commands.Cog.listener()
   async def on_member_remove(self, member):
      print(f'{member} has left the server.')

def setup (client):
   client.add_cog(Events(client))