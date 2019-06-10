import discord
from discord.ext import commands, tasks
import urllib.request, json
from datetime import datetime, timedelta

class SRC(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   @tasks.loop(minutes=10.0)
   async def checkPBs (self):
      with urllib.request.urlopen('https://www.speedrun.com/api/v1/users/18q2o608/personal-bests') as url:
         data = json.loads(url.read().decode())
         
      data = data['data']
      
      for record in data:
         verified_date = datetime.strptime(record['run']['status']['verify-date'][:10] + ' ' + record['run']['status']['verify-date'][11:-1], '%Y-%m-%d %H:%M:%S')
      
         #If verified less than an hour ago
         if record['run']['status']['status'] == 'verified' and datetime.utcnow() - timedelta(minutes=10) <= verified_date <= datetime.utcnow():
            link = record['run']['weblink']
            verified_date = verified_date.strftime('%b %#d, %Y at %H:%M')
            
            if record['place'] < 4:
               if record['place'] == 1:
                  place = str(record['place']) + 'st'
               elif record['place'] == 2:
                  place = str(record['place']) + 'nd'
               elif record['place'] == 3:
                  place = str(record['place']) + 'rd'
            else:
               place = str(record['place']) + 'th'
            
            sec, ms = divmod(record['run']['times']['primary_t'] * 100, 100)
            min, sec = divmod(sec, 60)
            hr, min = divmod(min, 60)
            
            ms = int(ms)
            sec = int(sec)
            min = int(min)
            hr = int(hr)
            
            if hr == 0:
               if min == 0:
                  time = f'{sec}.{ms}'
               else:
                  time = f'{min}:{sec}'
                  
                  if ms > 0:
                     time = time + f'.{ms}'
            else:
               time = f'{hr}:{min}:{sec}'
               
               if ms > 0:
                  time = time + f'.{ms}'
            
            for weblink in record['run']['links']:
               if weblink['rel'] == 'game':
                  gameurl = weblink['uri']
               if weblink['rel'] == 'category':
                  categoryurl = weblink['uri']
                  
            with urllib.request.urlopen(gameurl) as gameurl:
               gameinfo = json.loads(gameurl.read().decode())
            
            game = gameinfo['data']['names']['twitch']
            cover = gameinfo['data']['cover-large']['uri']
            
            with urllib.request.urlopen(categoryurl) as categoryurl:
               categoryinfo = json.loads(categoryurl.read().decode())
            
            category = categoryinfo['name']
            
            embed=discord.Embed(title=f'New Personal Best at {time}!', url=link, description=f'Will has set a new PB for {game} - {category} and is now {place} on the leaderboard.', color=0x55c5c6)
            embed.set_author(name='will-am-I', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
            embed.set_thumbnail(url=cover)
            embed.set_footer(text=f'Run verified {verified_date} UTC.')
            await self.client.send(embed=embed)
            
def setup (client):
   client.add_cog(SRC(client))