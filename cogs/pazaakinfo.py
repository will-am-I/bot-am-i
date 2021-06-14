import discord, json, MySQLdb
from discord.ext import commands, tasks

with open('./cogs/config.json') as data:
   config = json.load(data)

class PazaakInfo(commands.Cog):

   def __init__ (self, client):
      self.client = client

   @commands.command()
   async def pazaakrank (self, ctx):
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute(f"SELECT * FROM pazaak WHERE discordid = {ctx.message.author.id}")
         if cursor.rowcount > 0:
            cursor.execute("SELECT discordid, wins, losses FROM pazaak ORDER BY wins DESC, losses ASC")
            results = cursor.fetchall()
            
            i = 0
            for result in results:
               i += 1
               if result[0] == ctx.message.author.id:
                  place = str(i)
                  if place.endswith("1") and not place.endswith("11"):
                     place += "st"
                  elif place.endswith("2") and not place.endswith("12"):
                     place += "nd"
                  elif place.endswith("3") and not place.endswith("13"):
                     place += "rd"
                  else:
                     place += "th"

                  embed = discord.Embed(title=f"{ctx.message.author.name}'s Pazaak Rank", colour=discord.Colour(0x4e7e8a), description=f"You are {place} place on the leaderboard.")
                  embed.set_thumbnail(url=ctx.message.author.avatar_url)
                  embed.add_field(name="Wins", value=result[1])
                  embed.add_field(name="Losses", value=result[2])
                  await ctx.send(embed=embed)
                  break
         else:
            await ctx.send(f"{ctx.message.author.mention}, you currently don't have a pazaak rank since you have never played a game. Go to {self.client.get_channel(847627259275116554).mention} and start your first game!")
      except Exception as e:
         print(str(e))
      
      db.close()

   @commands.command()
   async def pazaaktop (self, ctx):
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute("SELECT m.discordname, p.wins, p.losses FROM pazaak p INNER JOIN member_rank m ON p.discordid = m.discordid ORDER BY p.wins DESC, p.losses ASC")
         if cursor.rowcount < 10:
            rows = cursor.rowcount
         else:
            rows = 10
         results = cursor.fetchall()

         leaderboard = ""
         for i in range(rows):
            leaderboard += f"**{i+1}.**\t{results[i][0]}\t{results[i][1]}/{results[i][2]}\n"

         await ctx.send(embed=discord.Embed(title="Pazaak Leaderboard", colour=discord.Colour(0x4e7e8a), description=leaderboard))
      except Exception as e:
         print(str(e))

      db.close()

   @commands.command()
   async def pazaakhelp (self, ctx, command=None, dmcommand=None):
      if command is None:
         embed = discord.Embed(title="How to play pazaak", colour=discord.Colour(0x4e7e8a), description="Type !pazaakhelp <command> for more information about each one or !pazaakhelp sidedeck for help in side deck selection.")
         embed.add_field(name="**!pazaak <member> [wager]**", value="Use this to challenge another member to a game of pazaak.", inline=False)
         embed.add_field(name="**!accept**", value="Use this to accept the pazaak challenge.", inline=False)
         embed.add_field(name="**!decline**", value="Use this to delcine the pazaak challenge.", inline=False)
         embed.add_field(name="**!heads**", value="Use this to choose heads for the coin flip to start the game.", inline=False)
         embed.add_field(name="**!tails**", value="Use this to choose tails for the coin flip to start the game.", inline=False)
         embed.add_field(name="**!end**", value="Use this to end your turn.", inline=False)
         embed.add_field(name="**!stand**", value="Use this to stand on your hand.", inline=False)
         embed.add_field(name="**!play <card> [sign]**", value="Use this to play one of your side deck cards.", inline=False)
         embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
         await ctx.send(embed=embed)
      elif command == "sidedeck":
         if dmcommand is None:
            embed = discord.Embed(title="Side deck selection", colour=discord.Colour(0x4e7e8a), description="The side deck is used to get your hand to 20 or as close as possible.\nYou first select 10 cards, and, out of those 10, 4 are randomly selected to be playable.\n\nThe following are commands to use in your DM with the bot, do not use '!' with these commands.\nType !pazaakhelp sidedeck <command> for help with these particular commands.")
            embed.add_field(name="add <card> [amount]", value="Use this to add one or more of a specific card to your side deck.", inline=False)
            embed.add_field(name="remove <card> [amount]", value="Use this to remove one or more of a specific card from your side deck.", inline=False)
            embed.add_field(name="last", value="Use this to bring up the last side deck you used.", inline=False)
            embed.add_field(name="done", value="Use this to finish your side deck selection and receive your playable cards.", inline=False)
            embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
            await ctx.send(embed=embed)
         elif dmcommand == "add":
            embed = discord.Embed(title="add <card> [amount]", colour=discord.Colour(0x4e7e8a), description="This is used to add one or more of a specific card to your side deck.")
            embed.add_field(name="<card>", value="This is the specific card you wish to add.\nAll cards must be typed inside '[]'.\n_(For example '[+4]' or '[F3/6]' or '[+/-3]'.)_", inline=False)
            embed.add_field(name="[amount]", value="This is the amount of cards you wish to add.\nIf no amount is entered, 1 will be added.\nYou man not add more cards than what you currently own.", inline=False)
            embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
            await ctx.send(embed=embed)
         elif dmcommand == "remove":
            embed = discord.Embed(title="remove <card> [amount]", colour=discord.Colour(0x4e7e8a), description="This is used to add one or more of a specific card to your side deck.")
            embed.add_field(name="<card>", value="This is the specific card you wish to remove.\nAll cards must be typed inside '[]'.\n_(For example '[+4]' or '[F3/6]' or '[+/-3]'.)_", inline=False)
            embed.add_field(name="[amount]", value="This is the amount of cards you wish to remove.\nIf no amount is entered, 1 will be removed.\nYou man not remove more cards than what you currently have selected.", inline=False)
            embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
            await ctx.send(embed=embed)
         elif dmcommand == "last":
            await ctx.send(embed=discord.Embed(title="last", colour=discord.Colour(0x4e7e8a), description="This is used to pull the last side deck you used.\nYou will still be free to remove and add cards, and you must still type done to confirm the side deck.\n\nIf you have not played a game before, you will not have a previously used side deck, and this command will not work."))
         elif dmcommand == "done":
            await ctx.send(embed=discord.Embed(title="done", colour=discord.Colour(0x4e7e8a), description="This is used to confirm your side deck.\nIf you have fewer than 10 cards, this will not work.\nAfter typing 'done', you will receive your 4 playable cards.\n\nOnce both players have confirmed their respective side decks, play will continue in the main pazaak play channel."))
         else:
            await ctx.send(f"{dmcommand} is not a side deck command.")
      elif command == "pazaak":
         embed = discord.Embed(title="!pazaak <member> [wager]", colour=discord.Colour(0x4e7e8a), description=f"This command is used to challenge another member to pazaak.\nThe challenge will expire after 3 minutes.\nBe sure to keep all pazaak play in {self.client.get_channel(847627259275116554).mention}.")
         embed.add_field(name="<member>", value="Tag another server member using @.", inline=False)
         embed.add_field(name="[wager]", value="Enter a numerical wager amount.\nThe amount must be more than 50 and both players must have the amount on hand.", inline=False)
         embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
         await ctx.send(embed=embed)
      elif command == "accept":
         await ctx.send(embed=discord.Embed(title="!accept", colour=discord.Colour(0x4e7e8a), description="This command is used to accept the pazaak challenge.\nYou will have 3 minutes from when the challenge was first made.\nOnce accepted both players will receive DM's to start the side deck selection."))
      elif command == "decline":
         await ctx.send(embed=discord.Embed(title="!decline", colour=discord.Colour(0x4e7e8a), description="This command is used to delcline the pazaak challenge.\nIf nothing happens after 3 minutes the challenge expires and is treated as if it was declined anyway."))
      elif command == "heads":
         await ctx.send(embed=discord.Embed(title="!heads", colour=discord.Colour(0x4e7e8a), description="This command is used to select heads for the initial coin flip.\nYou will get a prompt to do so when both players have selected their repective side decks."))
      elif command == "tails":
         await ctx.send(embed=discord.Embed(title="!tails", colour=discord.Colour(0x4e7e8a), description="This command is used to select tails for the initial coin flip.\nYou will get a prompt to do so when both players have selected their repective side decks."))
      elif command == "end":
         await ctx.send(embed=discord.Embed(title="!end", colour=discord.Colour(0x4e7e8a), description="This command is used to end your turn.\nThis will allow the next player to proceed with his turn unless he has typed !stand, in which case it will be your turn again.\nAfterwards play will return to you for your turn.\nIf your total reaches 20 at any time your turn will automatically end and acts as if you already typed !stand."))
      elif command == "stand":
         await ctx.send(embed=discord.Embed(title="!stand", colour=discord.Colour(0x4e7e8a), description="This command is used to stand on your hand.\nThis will allow the next player to play his turn unless he as also typed !stand.\nIf your total reaches 20 at any time your turn will automatically end and acts as if you already typed !stand."))
      elif command == "play":
         embed = discord.Embed(title="!play <card> [sign]", colour=discord.Colour(0x4e7e8a), description="This command is used to play a card from your side deck.\nCheck your DM's for your playable side deck.\nAfterwards you must still type !end or !stand for play to continue\nIf your total reaches 20 at any time your turn will automatically end and acts as if you already typed !stand.")
         embed.add_field(name="<card>", value="Type the card you wish to play surrounded by '[]'.\n_(For example, a '+4' card would be typed as '[+4]' and a '-1' card would be typed as '[-1]'.)_\nOther specialty cards will just take the first letter.\n_(For example, a Double card would be typed as '[D]' and a Flip 2/4 card would be typed as '[F2/4]'.)_", inline=False)
         embed.add_field(name="[sign]", value="Type '+' (plus) or '-' (minus) to determine if the played card will be plus or minus.\nThis is only used for +/- cards and the Tiebreaker card.\n_(For example, a '+/- 2' card to be negative will be typed as '[+/-2] -' and a tiebreaker card to be positive will be typed as '[T] +'.)_")
         embed.set_footer(text="Arguments with '<>' are required; arguments with '[]' are optional.")
         await ctx.send(embed=embed)
      else:
         await ctx.send(f"{command} is not a pazaak command.")

   @commands.command()
   async def pazaakdeck (self, ctx):
      cardOptions = ["+1", "+2", "+3", "+4", "+5", "+6", "-1", "-2", "-3", "-4", "-5", "-6", "+/-1", "+/-2", "+/-3", "+/-4", "+/-5", "+/-6", "Flip 2/4", "Flip 3/6", "Double", "Tiebreaker"]
      
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      cursor.execute(f"SELECT plus_one, plus_two, plus_three, plus_four, plus_five, plus_six, minus_one, minus_two, minus_three, minus_four, minus_five, minus_six, plus_minus_one, plus_minus_two, plus_minus_three, plus_minus_four, plus_minus_five, plus_minus_six, flip_two_four, flip_three_six, double_card, tiebreaker_card FROM pazaak WHERE discordid = {ctx.message.author.id}")

      if cursor.rowcount > 0:
         cardAmounts = cursor.fetchone()

         embed = discord.Embed(title="Your deck", colour=discord.Colour(0x4e7e8a))
         for i in range(len(cardOptions)):
            if "Flip" in cardOptions[i] or cardOptions[i] == "Double" or cardOptions[i] == "Tiebreaker":
               embed.add_field(name=f"[{cardOptions[i]}]", value=str(cardAmounts[i]), inline=False)
            else:
               embed.add_field(name=f"[{cardOptions[i]}]", value=str(cardAmounts[i]), inline=True)
         
         user = self.client.get_user(ctx.message.author.id)
         await user.send(embed=embed)
      else:
         ctx.send("You currently don't have a pazaak deck. Go play your first game of pazaak to obtain a deck.")
      
      db.close()

def setup (client):
   client.add_cog(PazaakInfo(client))