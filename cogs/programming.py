import discord, urllib.request, requests, json, MySQLdb
from discord.ext import commands
from datetime import datetime

WILL_ID = 320246151196704768
with open('./cogs/config.json') as data:
   config = json.load(data)

class Programming(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   #Test code
   @commands.command()
   async def test(self, ctx):
      if ctx.message.author.id == WILL_ID:
         #await ctx.message.author.send('Test')
         msg = await self.client.get_channel(834261336971673611).send(f"If you stream on Twitch and would like to have announcements in this discord when you go live react with :purple_heart:. (Be sure your twitch is connected in {self.client.get_channel(829917630579867759).mention})")
         await msg.add_reaction("💜")

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

   @commands.command()
   async def rules(self, ctx):
      if ctx.message.author.id == WILL_ID:
         embed = discord.Embed()
         embed.add_field(name=":one:", value="Treat everyone with respect. We're all humans and should support each other. Tattletaling is another form of disrespect, so please don't. Just be a decent person.", inline=False)
         embed.add_field(name=":two:", value="Keep political and religious opinions out. We are here for gaming and this is not the place for debates. Please take any discussions to DM's or another server.", inline=False)
         embed.add_field(name=":three:", value="No NSFW or obscene content. This includes text, images, or links featuring nudity, sex, hard violence, or other graphically disturbing content.", inline=False)
         embed.add_field(name=":four:", value="If you have to ask weather or not you can say something, just assume the answer is no. If you have any other questions or concerns, please bring them up to Will or the mods.", inline=False)
         embed.add_field(name=":five:", value="Have fun!", inline=False)
         await self.client.get_channel(829916638949408799).send(embed=embed)
   
def setup (client):
   client.add_cog(Programming(client))