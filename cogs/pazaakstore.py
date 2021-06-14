import discord, json, MySQLdb
from discord.ext import commands, tasks

with open('./cogs/config.json') as data:
   config = json.load(data)

class PazaakStore(commands.Cog):

   def __init__ (self, client):
      self.client = client

   @commands.command()
   async def pazaakstore (self, ctx, page=1):
      cardOptions = [["+1", "+2", "+3", "+4", "+5", "+6"], ["-1", "-2", "-3", "-4", "-5", "-6"], ["+/-1", "+/-2", "+/-3", "+/-4", "+/-5", "+/-6"], ["F2/4", "F3/6", "D", "T"]]
      cardPrices = [[200, 150, 100, 50, 25, 10], [200, 150, 100, 50, 25, 10], [400, 300, 250, 200, 150, 100], [700, 900, 750, 1200]]
      prestige = ["Must have won at least 10 games and played at least 30.", "Must have won at least 10 games and played at least 30.", "Must have won at least 20 games and played at least 50.", "Must have won at least 50 games and played at least 100."]
      specialCards = ["Flip 2/4", "Flip 3/6", "Double", "Tiebreaker"]
      
      description = "Use !pazaakbuy <card> to purchase a card."
      if page == 4:
         description += "\nOnly one of each of these cards per person."

      embed = discord.Embed(title="Card Store", colour=discord.Colour(0x4e7e8a), description=description)
      embed.set_footer(text=f"Page {page}/4 | Use !pazaakstore <page> to select another page.")

      i = page - 1
      for j in range(len(cardOptions[i])):
         if page < 4:
            embed.add_field(name=f"[{cardOptions[i][j]}]", value=f"{cardPrices[i][j]} credits", inline=True)
         else:
            embed.add_field(name=f"[{cardOptions[i][j]}] {specialCards[j]}", value=f"{cardPrices[i][j]} credits\n{prestige[j]}", inline=False)

      await ctx.send(embed=embed)

   @commands.command()
   async def pazaakbuy (self, ctx, card):
      cards = {"+1": ["plus_one", 200], "+2": ["plus_two", 150], "+3": ["plus_three", 100], "+4": ["plus_four", 50], "+5": ["plus_five", 25], "+6": ["plus_six", 10], "-1": ["minus_one", 200], "-2": ["minus_two", 150], "-3": ["minus_three", 100], "-4": ["minus_four", 50], "-5": ["minus_five", 25], "-6": ["minus_six", 10], "+/-1": ["plus_minus_one", 400], "+/-2": ["plus_minus_two", 300], "+/-3": ["plus_minus_three", 250], "+/-4": ["plus_minus_four", 200], "+/-5": ["plus_minus_five", 150], "+/-6": ["plus_minus_six", 100], "F2/4": ["flip_two_four", 700], "F3/6": ["flip_three_six", 900], "D": ["double_card", 750], "T": ["tiebreaker_card", 1200]}
      specialCards = {"F2/4": [10, 30], "F3/6": [10, 30], "D": [20, 50], "T": [50, 100]}
      card = card.translate({ord(i): None for i in '[]'})

      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute(f"SELECT * FROM pazaak WHERE discordid = {ctx.message.author.id}")

         if cursor.rowcount == 0:
            await ctx.send("You don't currently have a deck of your own. Play your first game of pazaak to obtain a deck.")
         else:
            cursor.execute(f"SELECT coins FROM member_rank WHERE discordid = {ctx.message.author.id}")
            credits = cursor.fetchone()[0]

            if credits >= cards[card][1]:
               if card in specialCards:
                  cursor.execute(f"SELECT wins, wins + losses AS games FROM pazaak WHERE discordid = {ctx.message.author.id}")
                  results = cursor.fetchone()
                  
                  if results[1] < specialCards[card][1]:
                     await ctx.send("You have not played enough games to buy this card.")
                  elif results[0] < specialCards[card][0]:
                     await ctx.send("You have not won enough games to buy this card.")
                  else:
                     cursor.execute(f"UPDATE member_rank SET coins = coins - {cards[card][1]} WHERE discordid = {ctx.message.author.id}")
                     db.commit()
                     cursor.execute(f"UPDATE pazaak SET {cards[card][0]} = {cards[card][0]} + 1 WHERE discordid = {ctx.message.author.id}")
                     db.commit()
                     await ctx.send(f"[{card}] has been added to your deck.")
               else:
                  cursor.execute(f"UPDATE member_rank SET coins = coins - {cards[card][1]} WHERE discordid = {ctx.message.author.id}")
                  db.commit()
                  cursor.execute(f"UPDATE pazaak SET {cards[card][0]} = {cards[card][0]} + 1 WHERE discordid = {ctx.message.author.id}")
                  db.commit()
                  await ctx.send(f"[{card}] has been added to your deck.")
            else:
               await ctx.send("You don't have enough credits for this card.")
      except Exception as e:
         db.rollback()
         print(str(e))

      db.close()

def setup (client):
   client.add_cog(PazaakStore(client))