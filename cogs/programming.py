import discord
from discord.ext import commands

WILL_ID = 320246151196704768

class Programming(commands.Cog):
   
   def __init__ (self, client):
      self.client = client
   
   @commands.command()
   async def test(self, ctx):
      if ctx.message.author.id == WILL_ID:
         embed=discord.Embed(title='Sunshine Any% World Record Attempts', url='https://www.twitch.tv/samura1man', description='', color=0x55c5c6)
         embed.set_author(name='samura1man', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
         embed.set_thumbnail(url='https://static-cdn.jtvnw.net/ttv-boxart/Super%20Mario%20Sunshine-272x380.jpg')
         embed.set_image(url='https://static-cdn.jtvnw.net/previews-ttv/live_user_samura1man-640x360.jpg')
         embed.add_field(name='Game', value='Super Mario Sunshine')
         await ctx.send(embed=embed)
   
   @commands.command(aliases=['textid'])
   async def textchannelid(self, ctx, channel : discord.TextChannel):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{channel.id}')

   @commands.command()
   async def roleid(self, ctx, role : discord.Role):
      if ctx.message.author.id == WILL_ID:
         await ctx.send(f'{role.id}')
   
def setup (client):
   client.add_cog(Programming(client))