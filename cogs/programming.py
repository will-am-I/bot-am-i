import discord, urllib.request, json, requests
from discord.ext import commands
from random import randint

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
         url = 'https://api.twitch.tv/helix/streams?user_login=bobross'
         header = {'Client-ID': config['twitch_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
         request = urllib.request.Request(url, headers=header)
         with urllib.request.urlopen(request) as streamurl:
            streaminfo = json.loads(streamurl.read().decode())

         streaminfo = streaminfo['data'][0]
         gameid = streaminfo['game_id']
         title = streaminfo['title']
         thumbnail = streaminfo['thumbnail_url'].replace('{width}', '640').replace('{height}', '360') + f'?rand={randint(0, 999999)}'
         print(thumbnail)

         request = urllib.request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header)
         with urllib.request.urlopen(request) as gameurl:
            gameinfo = json.loads(gameurl.read().decode())
         gameinfo = gameinfo['data'][0]
         game = gameinfo['name']
         cover = gameinfo['box_art_url'].replace('{width}', '272').replace('{height}', '380').replace('/./', '/') + f'?rand={randint(0, 999999)}'
         print(cover)
         
         request = urllib.request.Request('https://api.twitch.tv/helix/users?login=bobross', headers=header)
         with urllib.request.urlopen(request) as userurl:
            userinfo = json.loads(userurl.read().decode())
         userinfo = userinfo['data'][0]
         description = userinfo['description']
         icon = userinfo['profile_image_url']

         embed=discord.Embed(title=title, url='https://www.twitch.tv/bobross', description=description, color=0x55c5c6)
         embed.set_author(name='Soberlyte', icon_url=icon)
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