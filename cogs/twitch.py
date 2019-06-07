import discord
from discord.ext import commands, tasks
import urllib.request, json
from datetime import datetime, timedelta

token = 'krc091qnndbsa5oyys1n24hirkq5nr'
client_id = '0o51ky43x9haa5pp5lpdy4p1zwbvz7'

class SRC(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   @tasks.loop(minutes=5.0)
   async def checkPBs (self):
      url = 'https://api.twitch.tv/helix/streams?user_login=will_am_I_'
      header = {'Client-ID': client_id}
      request = urllib.request.Request(url, headers=header)

      with urllib.request.urlopen(request) as streamurl:
         streaminfo = json.loads(streamurl.read().decode())

      if streaminfo['data']:
         streaminfo = streaminfo['data'][0]

         if datetime.utcnow() - timedelta(minutes=5) <= datetime.strptime(streaminfo['started_at'][:10] + ' ' + streaminfo['started_at'][11:-1], '%Y-%m-%d %H:%M:%S') <= datetime.utcnow():
            gameid = streaminfo['game_id']
            title = streaminfo['title']


      #embed=discord.Embed(title=f'Will is now live on Twitch!', url=link, description=streamtitle, color=0x55c5c6)
      #embed.set_author(name='will-am-I', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
      #embed.set_thumbnail(url=cover)
      #embed.set_footer(text=f'Run verified {verified_date} UTC.')
      #await self.client.send(embed=embed)
   
def setup (client):
   client.add_cog(SRC(client))