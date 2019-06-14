import discord
from discord.ext import commands, tasks
import urllib.request, json
from datetime import datetime, timedelta

class SRC(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkPersonalBests.start()

   def cog_unload (self):
      self.checkPersonalBests.stop()
   
   @tasks.loop(minutes=15.0)
   async def checkPersonalBests (self):
      print("src -> loop")
      with urllib.request.urlopen('https://www.speedrun.com/api/v1/users/18q2o608/personal-bests') as pbjson:
         data = json.loads(pbjson.read().decode())['data']
         
      for record in data:
         print("src -> pb record")
         link = ''
         place = ''
         time = ''
         gameurl = ''
         categoryurl = ''
         levelurl = ''
         category = ''
         level = ''
         levelid = ''
         stage = ''
         stageid = ''

         verified_date = datetime.strptime(record['run']['status']['verify-date'][:10] + ' ' + record['run']['status']['verify-date'][11:-1], '%Y-%m-%d %H:%M:%S')
      
         #If verified less than 15 minutes ago
         if record['run']['status']['status'] == 'verified' and datetime.utcnow() - timedelta(minutes=15) <= verified_date <= datetime.utcnow():
            print("src -> found new pb")
            link = record['run']['weblink']
            verified_date = verified_date.strftime('%b %#d, %Y at %H:%M')
            place = str(record['place'])

            if place.endswith("1") and place != "11":
               place = place + 'st'
            elif place.endswith("2") and place != "12":
               place = place + 'nd'
            elif place.endswith("3") and place != "13":
               place = place + 'rd'
            else:
               place = place + 'th'

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
               if weblink['rel'] == 'level':
                  levelurl = weblink['uri']

            with urllib.request.urlopen(gameurl) as gamejson:
               gameinfo = json.loads(gamejson.read().decode())
            
            game = gameinfo['data']['names']['twitch']
            cover = gameinfo['data']['assets']['cover-large']['uri']
            
            if levelurl != '':
               print("src -> level info")
               levelid = list(record['run']['values'].keys())[0]
               stageid = record['run']['values'][levelid]

               with urllib.request.urlopen(levelurl) as leveljson:
                  levelinfo = json.loads(leveljson.read().decode())

               level = levelinfo['data']['name']

               with urllib.request.urlopen(levelurl + '/variables') as stagejson:
                  stageinfo = json.loads(stagejson.read().decode())

               stage = stageinfo['data'][0]['values']['choices'][stageid]

               category = f'{level} ({stage})'
            else:
               print("src -> category info")
               with urllib.request.urlopen(categoryurl) as categoryjson:
                  categoryinfo = json.loads(categoryjson.read().decode())
            
               category = categoryinfo['name']
            
            embed=discord.Embed(title=f'New Personal Best at {time}!', url=link, description=f'Will has set a new PB for {game} - {category} and is now {place} on the leaderboard.', color=0x55c5c6)
            embed.set_author(name='will-am-I', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
            embed.set_thumbnail(url=cover)
            embed.set_footer(text=f'Run verified {verified_date} UTC.')
            await self.client.get_channel(588934917551947787).send(embed=embed)
            print("src -> posted new pb")
            
def setup (client):
   client.add_cog(SRC(client))