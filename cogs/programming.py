import discord, json
from discord.ext import commands
from twitch import TwitchHelix
from random import randint

with open('./cogs/config.json') as data:
   config = json.load(data)

WILL_ID = 320246151196704768
twitch_client = TwitchHelix(client_id=config['twitch_id'], oauth_token=config['twitch_token'])

class Programming(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   #Test code
   @commands.command()
   async def test(self, ctx):
      if ctx.message.author.id == WILL_ID:
         stream = twitch_client.get_streams(user_logins='bobross')
         stream = stream[0]
         gameid = stream['game_id']
         title = stream['title']
         thumbnail = stream['thumbnail_url'].replace('{width}', '640').replace('{height}', '360') + f'?rand={randint(0, 999999)}'

         gameinfo = twitch_client.get_games(game_ids=gameid)
         gameinfo = gameinfo[0]
         game = gameinfo['name']
         cover = gameinfo['box_art_url'].replace('{width}', '272').replace('{height}', '380') + f'?rand={randint(0, 999999)}'

         embed = discord.Embed(title=title, url='https://www.twitch.tv/bobross')
         embed.set_thumbnail(url=cover)
         embed.set_image(url=thumbnail)
         embed.add_field(name='Game', value=game)
         await ctx.send(embed=embed)
   
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