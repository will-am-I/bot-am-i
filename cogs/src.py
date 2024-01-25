import discord, urllib.request, json, mysql.connector
from discord.ext import commands, tasks
from datetime import datetime
from random import randint

with open('./cogs/config.json') as data:
   config = json.load(data)

class SRC(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.checkPersonalBests.start()

   def cog_unload (self):
      self.checkPersonalBests.cancel()
   
   @tasks.loop(minutes=10)
   async def checkPersonalBests (self):
      print("\n")
      print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
      print("src -> loop")
      db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
      cursor = db.cursor()

      try:
         runs = []
         cursor.execute("SELECT runid FROM src_pbs")
         results = cursor.fetchall()
         for id in results:
            runs.append(id[0])
         with urllib.request.urlopen('https://www.speedrun.com/api/v1/users/18q2o608/personal-bests') as pbjson:
            data = json.loads(pbjson.read().decode())['data']

         currentpbs = []
         for record in data:
            verified_date = datetime.strptime(record['run']['status']['verify-date'][:10] + ' ' + record['run']['status']['verify-date'][11:-1], '%Y-%m-%d %H:%M:%S')
            levelurl = None

            currentpbs.append(record['run']['id'])

            if record['run']['id'] not in runs:
               print("src -> found new pb -> " + record['run']['id'])
               cursor.execute(f"INSERT INTO src_pbs (runid, gameid, categoryid, levelid, verified, submitted) VALUES ('{record['run']['id']}', '{record['run']['game']}', '{record['run']['category']}', '{record['run']['level']}', STR_TO_DATE('{record['run']['status']['verify-date'][:10] + ' ' + record['run']['status']['verify-date'][11:-1]}', '%Y-%m-%d %T'), STR_TO_DATE('{record['run']['submitted'][:10] + ' ' + record['run']['submitted'][11:-1]}', '%Y-%m-%d %T'))")

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

               se, ms = divmod(record['run']['times']['primary_t'] * 100, 100)
               mi, se = divmod(se, 60)
               hr, mi = divmod(mi, 60)
               
               ms = str(int(ms)).ljust(2, '0')
               se = str(int(se)).zfill(2)
               mi = str(int(mi)).zfill(2)
               hr = str(int(hr))
               
               if int(hr) == 0:
                  if int(mi) == 0:
                     time = f'{se}.{ms}'
                  else:
                     time = f'{mi}:{se}'
                     
                     if int(ms) > 0:
                        time = time + f'.{ms}'
               else:
                  time = f'{hr}:{mi}:{se}'
                  
                  if int(ms) > 0:
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
               cover = gameinfo['data']['assets']['cover-large']['uri'] + f'?rand={randint(0, 999999)}'
               
               if levelurl is not None:
                  print("src -> level info")

                  with urllib.request.urlopen(levelurl) as leveljson:
                     levelinfo = json.loads(leveljson.read().decode())

                  with urllib.request.urlopen(levelurl + '/variables') as stagejson:
                     stageinfo = json.loads(stagejson.read().decode())

                  if len(record['run']['values']) > 0:
                     variables = ""
                     i = 1
                     
                     for variable in stageinfo['data']:
                        if variable['is-subcategory'] == True and variable['id'] in list(record['run']['values'].keys()):
                           variables += variable['values']['values'][record['run']['values'][variable['id']]]['label'] + ", "
                           cursor.execute(f"UPDATE src_pbs SET variableid{i} = '{record['run']['values'][variable['id']]}' WHERE runid = '{record['run']['id']}'")
                           i += 1
                     
                     category = f"{levelinfo['data']['name']} ({variables[:-2]})"
                  else:
                     category = levelinfo['data']['name']
               else:
                  print("src -> category info")
                  with urllib.request.urlopen(categoryurl) as categoryjson:
                     categoryinfo = json.loads(categoryjson.read().decode())
                  
                  if len(record['run']['values']) > 0:
                     subcategories = ""
                     i = 1

                     with urllib.request.urlopen(categoryurl + '/variables') as subcategoryjson:
                        subcategoryinfo = json.loads(subcategoryjson.read().decode())
                     
                     for subcategory in subcategoryinfo['data']:
                        if subcategory['is-subcategory'] == True and subcategory['id'] in list(record['run']['values'].keys()):
                           subcategories += subcategory['values']['values'][record['run']['values'][subcategory['id']]]['label'] + ", "
                           cursor.execute(f"UPDATE src_pbs SET variableid{i} = '{record['run']['values'][subcategory['id']]}' WHERE runid = '{record['run']['id']}'")
                           i += 1

                     category = f"{categoryinfo['data']['name']} ({subcategories[:-2]})"
                  else:
                     category = categoryinfo['data']['name']

               embed=discord.Embed(title=f'New Personal Best at {time}!', url=link, description=f'Will has set a new PB for\n**{game}** - ***{category}***\nand is now {place} on the leaderboard.', color=0x55c5c6)
               embed.set_author(name='will-am-I', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
               embed.set_thumbnail(url=cover)
               embed.set_footer(text=f'Run verified {verified_date} UTC.')
               await self.client.get_channel(588934917551947787).send(content='<@&583864250410336266>', embed=embed)
               print("src -> posted new pb")
            else:
               print("pb -> " + record['run']['id'])

         for run in runs:
            if run not in currentpbs:
               cursor.execute(f"DELETE FROM src_pbs WHERE runid = '{run}'")

         db.commit()
      except Exception as e:
         db.rollback()
         print(str(e))
      
      db.close()
            
async def setup (client):
   print("SRC loaded")
   await client.add_cog(SRC(client))