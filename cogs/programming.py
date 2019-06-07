import discord
from discord.ext import commands

WILL_ID = 320246151196704768

class Programming(commands.Cog):
   def __init__ (self, client):
      self.client = client
   
   @commands.command()
   async def test(self, ctx):
      if ctx.message.author.id == WILL_ID:
         await ctx.send('Hello')
      #await ctx.send(f'{ctx.message.author.id}')
   
   @commands.command(aliases=['textid'])
   async def textchannelid(self, ctx, channel : discord.TextChannel):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{channel.id}')
   
def setup (client):
   client.add_cog(Programming(client))