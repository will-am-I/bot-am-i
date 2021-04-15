import discord, urllib.request, requests, json, MySQLdb
from discord.ext import commands
from datetime import datetime

WILL_ID = 320246151196704768

class Programming(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   #Test code
   @commands.command()
   async def test(self, ctx):
      if ctx.message.author.id == WILL_ID:
         await ctx.message.author.send('Test')

   #Get Text Channel ID
   @commands.command(aliases=['textid'])
   async def textchannelid(self, ctx, channel : discord.TextChannel):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{channel.id}')

   #Get Role ID
   @commands.command()
   async def roleid(self, ctx, role : discord.Role):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{role.id}')

   #Get Voice Channel ID
   @commands.command(aliases=['voiceid'])
   async def voicechannelid(self, ctx, channel : discord.VoiceChannel):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{channel.id}')
   
def setup (client):
   client.add_cog(Programming(client))