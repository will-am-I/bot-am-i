import discord, json, MySQLdb, re
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from random import randint

with open('./cogs/config.json') as data:
   config = json.load(data)

PLAYER_1 = 0
PLAYER_2 = 1
TIED = -1

class Player:
   def __init__ (self, id, name, mention):
      self.id = id
      self.name = name
      self.mention = mention
      self.selection = []
      self.sideDeck = []
      self.fieldCards = []
      self.points = 0
      self.tiebreaker = False
      self.stood = False
      self.finishedSelection = False
      
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute(f"SELECT * FROM pazaak WHERE discordid = {id}")
         if cursor.rowcount == 0:
            cursor.execute(f"INSERT INTO pazaak (discordid) VALUES ({id})")
         db.commit()
      except Exception as e:
         db.rollback()
         print(str(e))
      
      db.close()

   def setSideDeck (self, sideDeck):
      self.sideDeck = sideDeck

   def finishSelection (self):
      self.finishedSelection = True

   def playCard (self, value=0, card=None):
      if card is None:
         self.fieldCards.append(value)
      else:
         self.sideDeck.remove(card)
         
         if card == "F2/4":
            values = [2,4,-2,-4]
            for i, fieldCard in enumerate(self.fieldCards):
               if fieldCard in values:
                  self.fieldCards[i] *= -1
         elif card == "F3/6":
            values = [3,6,-3,-6]
            for i, fieldCard in enumerate(self.fieldCards):
               if fieldCard in values:
                  self.fieldCards[i] *= -1
         elif card == "D":
            self.fieldCards.append(self.fieldCards[len(self.fieldCards) - 1])
         elif card == "T":
            self.tiebreaker = True
            self.fieldCards.append(value)
         else:
            self.fieldCards.append(value)

   def stand (self):
      self.stood = True

   def addSelection (self, card):
      if len(self.selection) < 10:
         self.selection.append(card)

   def removeSelection (self, card):
      self.selection.remove(card)

   def total (self):
      total = 0
      for cardValue in self.fieldCards:
         total += cardValue
      return total

   def wonRound (self):
      self.points += 1
      print(self.points)

   def clearBoard (self):
      self.fieldCards = []
      self.tiebreaker = False
      self.stood = False

class Game:
   def __init__ (self, player1, player2, bet):
      self.players = [Player(player1.id, player1.name, player1.mention), Player(player2.id, player2.name, player2.mention)]
      self.bet = bet
      self.round = 1
      self.currentPlayer = -1
      self.roundWinner = -1
      self.roundStarter = -1
      self.playedCards = []
      self.gameWinner = -1
      self.gameLoser = -1

   def getCurrentPlayerID (self):
      return self.players[self.currentPlayer].id

   def mentionCurrentPlayer (self):
      return self.players[self.currentPlayer].mention

   def showCardOptions (self, player):
      cardOptions = ["+1", "+2", "+3", "+4", "+5", "+6", "-1", "-2", "-3", "-4", "-5", "-6", "+/-1", "+/-2", "+/-3", "+/-4", "+/-5", "+/-6", "Flip 2/4", "Flip 3/6", "Double", "Tiebreaker"]

      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      cursor.execute(f"SELECT plus_one, plus_two, plus_three, plus_four, plus_five, plus_six, minus_one, minus_two, minus_three, minus_four, minus_five, minus_six, plus_minus_one, plus_minus_two, plus_minus_three, plus_minus_four, plus_minus_five, plus_minus_six, flip_two_four, flip_three_six, double_card, tiebreaker_card FROM pazaak WHERE discordid = {self.players[player].id}")
      cardAmounts = cursor.fetchone()

      embed = discord.Embed(title="Choose your side deck", colour=discord.Colour(0x4e7e8a), description="You may choose up to 10 cards, and 4 will be chosen at random to play.")
      for i in range(len(cardOptions)):
         if "Flip" in cardOptions[i] or cardOptions[i] == "Double" or cardOptions[i] == "Tiebreaker":
            embed.add_field(name=f"[{cardOptions[i]}]", value=str(cardAmounts[i]), inline=False)
         else:
            embed.add_field(name=f"[{cardOptions[i]}]", value=str(cardAmounts[i]), inline=True)
      
      db.close()

      return embed

   def canAddCards (self, player, card, amount):
      cards = {"+1": "plus_one", "+2": "plus_two", "+3": "plus_three", "+4": "plus_four", "+5": "plus_five", "+6": "plus_six", "-1": "minus_one", "-2": "minus_two", "-3": "minus_three", "-4": "minus_four", "-5": "minus_five", "-6": "minus_six", "+/-1": "plus_minus_one", "+/-2": "plus_minus_two", "+/-3": "plus_minus_three", "+/-4": "plus_minus_four", "+/-5": "plus_minus_five", "+/-6": "plus_minus_six", "F2/4": "flip_two_four", "F3/6": "flip_three_six", "D": "double_card", "T": "tiebreaker_card"}

      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      cursor.execute(f"SELECT {cards[card]} FROM pazaak WHERE discordid = {self.players[player].id}")
      amountOwned = cursor.fetchone()[0]

      selected = 0
      for selectedCard in self.players[player].selection:
         if selectedCard == card:
            selected += 1

      return amount + selected <= amountOwned

   def canRemoveCards (self, player, card, amount):
      selected = 0
      for selectedCard in self.players[player].selection:
         if selectedCard == card:
            selected += 1

      return selected >= amount

   def makeSelection (self, player, card, action):
      if action == "add":
         self.players[player].addSelection(card)
      if action == "remove":
         self.players[player].removeSelection(card)

   def showSelection (self, player):
      deck = ""
      count = 0
      for card in self.players[player].selection:
         deck += f"\n[{card}]\n"
         count += 1
      deck += f"\nTotal cards: {count}"

      return discord.Embed(title="Your current selection:", colour=discord.Colour(0x4e7e8a), description=deck)

   def finishSelection (self, player):
      cards = {"+1": "plus_one", "+2": "plus_two", "+3": "plus_three", "+4": "plus_four", "+5": "plus_five", "+6": "plus_six", "-1": "minus_one", "-2": "minus_two", "-3": "minus_three", "-4": "minus_four", "-5": "minus_five", "-6": "minus_six", "+/-1": "plus_minus_one", "+/-2": "plus_minus_two", "+/-3": "plus_minus_three", "+/-4": "plus_minus_four", "+/-5": "plus_minus_five", "+/-6": "plus_minus_six", "F2/4": "flip_two_four", "F3/6": "flip_three_six", "D": "double_card", "T": "tiebreaker_card"}

      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()
      try:
         cursor.execute(f"DELETE FROM pazaak_last_deck WHERE discordid = {self.players[player].id}")
         cursor.execute(f"INSERT INTO pazaak_last_deck (discordid) VALUES ({self.players[player].id})")
         for selected in self.players[player].selection:
            cursor.execute(f"UPDATE pazaak_last_deck SET {cards[selected]} = {cards[selected]} + 1 WHERE discordid = {self.players[player].id}")
         db.commit()
      except Exception as e:
         db.rollback()
         print(str(e))
      db.close()

      self.players[player].finishSelection()

   def finishedSelection (self, player):
      return self.players[player].finishedSelection

   def completedSideDeck (self, player):
      return len(self.players[player].selection) == 10

   def showPlayableCards (self, player):
      selected = []
      cards = []
      while True:
         rand = randint(0, 9)
         if rand not in selected:
            selected.append(rand)
            cards.append(self.players[player].selection[rand])
         if len(selected) == 4:
            break
      self.players[player].setSideDeck(cards)
      
      deck = ""
      for card in cards:
         deck += f"\n[{card}]\n"

      return discord.Embed(title="Your playable cards:", colour=discord.Colour(0x4e7e8a), description=deck)

   def hasCardsLeft (self, player):
      return len(self.players[player].sideDeck) > 0

   def showCurrentCards (self, player):
      deck = ""
      for card in self.players[player].sideDeck:
         deck += f"\n[{card}]\n"

      return discord.Embed(title="Your playable cards:", colour=discord.Colour(0x4e7e8a), description=deck)

   def coinToss (self, side):
      sides = ['heads', 'tails']
      result = sides[randint(0,1)]

      if side[0] == result[0]:
         self.roundStarter = self.currentPlayer = PLAYER_1
      else:
         self.roundStarter = self.currentPlayer = PLAYER_2

      return f"The coin landed on {result}. {self.players[self.currentPlayer].mention} will start the game."

   def setCard (self, value, playerCard=False, card=None):
      if playerCard:
         self.players[self.currentPlayer].playCard(value, card)
      else:
         while True:
            count = 0
            for played in self.playedCards:
               if played == value:
                  count += 1
            if count < 4:
               break
            else:
               value = randint(1,10)
         self.playedCards.append(card)

         self.players[self.currentPlayer].playCard(value)

   def canPlayCard (self, card):
      return card in self.players[self.currentPlayer].sideDeck

   def endTurn (self):
      if self.currentPlayer == PLAYER_1 and not self.players[PLAYER_2].stood:
         self.currentPlayer = PLAYER_2
      elif self.currentPlayer == PLAYER_2 and not self.players[PLAYER_1].stood:
         self.currentPlayer = PLAYER_1

   def stand (self):
      if self.currentPlayer == PLAYER_1:
         self.players[PLAYER_1].stand()
         if not self.players[PLAYER_2].stood:
            self.currentPlayer = PLAYER_2
      elif self.currentPlayer == PLAYER_2:
         self.players[PLAYER_2].stand()
         if not self.players[PLAYER_1].stood:
            self.currentPlayer = PLAYER_1

   def turnOver (self):
      if self.players[self.currentPlayer].total() == 20:
         return True
      elif len(self.players[self.currentPlayer].fieldCards) == 9:
         return True
      else:
         return False

   def roundOver (self):
      if self.players[PLAYER_1].total() > 20 or self.players[PLAYER_2].total() > 20:
         return True
      elif self.players[PLAYER_1].stood and self.players[PLAYER_2].stood:
         return True
      elif len(self.players[PLAYER_1].fieldCards) == 9 or len(self.players[PLAYER_2].fieldCards) == 9:
         return True
      else:
         return False

   def findRoundWinner (self):
      p1Total = self.players[PLAYER_1].total()
      p2Total = self.players[PLAYER_2].total()

      if p1Total > 20:
         self.roundWinner = PLAYER_2
      elif p2Total > 20:
         self.roundWinner = PLAYER_1
      elif len(self.players[PLAYER_1].fieldCards) == 9:
         self.roundWinner = PLAYER_1
      elif len(self.players[PLAYER_2].fieldCards) == 9:
         self.roundWinner = PLAYER_2
      elif p1Total > p2Total:
         self.roundWinner = PLAYER_1
      elif p1Total < p2Total:
         self.roundWinner = PLAYER_2
      elif self.players[PLAYER_1].tiebreaker:
         self.roundWinner = PLAYER_1
      elif self.players[PLAYER_2].tiebreaker:
         self.roundWinner = PLAYER_2
      else:
         self.roundWinner = TIED

   def declareRoundWinner (self):
      self.players[self.roundWinner].wonRound()
      return f"{self.players[self.roundWinner].mention} has won the round!"

   def nextRound (self):
      self.round += 1
      self.playedCards = []
      if self.roundWinner != TIED:
         self.roundStarter = self.currentPlayer = self.roundWinner
      else:
         self.currentPlayer = self.roundStarter
      self.players[PLAYER_1].clearBoard()
      self.players[PLAYER_2].clearBoard()
      self.setCard(randint(1,10))

      return f"{self.players[self.currentPlayer].mention} will start the next round."

   def displayBoard (self):
      embed = discord.Embed(title="Current Board", colour=discord.Colour(0x4e7e8a), description=f"{self.players[self.currentPlayer].name}'s turn.")

      for player in self.players:
         playerBoard = ""
         for i in range(9):
            if i >= len(player.fieldCards):
               playerBoard += "[  ]"
            else:
               playerBoard += f"[{player.fieldCards[i]}]"
            if (i + 1) % 3 == 0:
               playerBoard += "\n\n"
            else:
               playerBoard += "\t"
         playerBoard += f"Total: [{player.total()}]\n\nWins:\n"
         
         for i in range(3):
            if i < player.points:
               playerBoard += "[X] "
            else:
               playerBoard += "[ ] "
         embed.add_field(name=player.name, value=playerBoard, inline=True)

      return embed

   def gameOver (self):
      if self.players[PLAYER_1].points == 3:
         self.gameWinner = PLAYER_1
         self.gameLoser = PLAYER_2
         return True
      elif self.players[PLAYER_2].points == 3:
         self.gameWinner = PLAYER_2
         self.gameLoser = PLAYER_1
         return True
      else:
         return False

   def declareGameWinner (self):
      db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute(f"UPDATE member_rank SET coins = coins + {self.bet} WHERE discordid = {self.players[self.gameWinner].id}")
         cursor.execute(f"UPDATE member_rank SET coins = coins - {self.bet} WHERE discordid = {self.players[self.gameLoser].id}")
         cursor.execute(f"UPDATE pazaak SET wins = wins + 1 WHERE discordid = {self.players[self.gameWinner].id}")
         cursor.execute(f"UPDATE pazaak SET losses = losses + 1 WHERE discordid = {self.players[self.gameLoser].id}")
         db.commit()
      except Exception as e:
         db.rollback()
         print(str(e))
      db.close()

      return f"{self.players[self.gameWinner].mention} has won the game! {self.bet} coins have been awarded from {self.players[self.gameLoser].mention}!"

class Pazaak(commands.Cog):

   def __init__ (self, client):
      self.client = client
      self.player1 = None
      self.player2 = None
      self.challengeTime = datetime.utcnow()
      self.game = None
      self.finishedSelection = False
      self.cardPlayed = False
      self.bet = 0
      self.content = "Type !end to end your turn, !stand to keep your hand, or !play <card> <+/-> to play one of your side deck cards.\nTo play a side deck card be sure to use the brackets and only put '+' or '-' after if the card is a '+/-' card or tiebreaker card.\nFor example \"!play [+2]\" or \"!play [+/-4] -\" or \"!play [T] +\"."

   @commands.command()
   async def pazaak (self, ctx, player2 : discord.Member = None, bet="50"):
      if ctx.message.channel.id == 847627259275116554:
         if player2 is None:
            await ctx.send("Please tag the member you'd like to challenge.")
         elif self.game is not None:
            await ctx.send(f"{ctx.message.author.mention}, a game is already in progress. Please wait for this to finish before starting another one.")
         else:
            player1 = ctx.message.author
            wager = int(bet)

            if wager < 50:
               await ctx.send(f"{player1.mention}, you have to bet at least 50 credits to play pazaak.")
            else:
               db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
               cursor = db.cursor()

               try:
                  cursor.execute(f"SELECT coins FROM member_rank WHERE discordid = {player1.id}")
                  p1coins = cursor.fetchone()[0]
                  cursor.execute(f"SELECT coins FROM member_rank WHERE discordid = {player2.id}")
                  p2coins = cursor.fetchone()[0]

                  if wager > p1coins and wager > p2coins:
                     await ctx.send(f"{player1.mention}, neither you nor {player2.mention} have enough credits for a {wager}-credit bet.")
                  elif wager > p1coins:
                     await ctx.send(f"{player1.mention}, you don't have enough credits to bet {wager} credits.")
                  elif wager > p1coins:
                     await ctx.send(f"{player1.mention}, {player2.mention} doesn't have enough credits to bet {wager} credits.")
                  else:
                     self.player1 = player1
                     self.player2 = player2
                     self.challengeTime = datetime.utcnow()
                     self.bet = wager
                     await ctx.send(f"{player2.mention}, {player1.mention} has challenged you to a game of pazaak! Type !accept to accept the challenge or !decline to decline the challenge. The challenge expires after 3 minutes.")
               except Exception as e:
                  print(str(e))
               db.close()
   
   @commands.command()
   async def accept (self, ctx):
      if datetime.utcnow() - timedelta(minutes=3) > self.challengeTime:
         await ctx.send(f"{ctx.message.author.mention}, the challenge time has expired. Make a new challenge by typing !pazaak and tagging your opponent.")
      else:
         if ctx.message.author.id != self.player2.id:
            await ctx.send(f"{ctx.message.author.mention}, you can't accept the challenge for {self.player2.mention}.")
         else:
            self.game = Game(self.player1, self.player2, self.bet)
            await ctx.send(f"{self.player1.mention}, {self.player2.mention} has accepted the challenge! Please see your DM's for side deck selection.")

            content = "Type 'add' or 'remove', the cards you want as shown in brackets, inlcude the brackets, and the number of cards to add or remove (for example: \"add [+/-3] 2\" or \"remove [-2] 1\").\nFor special cards type \"[T]\" for Tiebreaker, \"[D]\" for Double, \"[F2/4]\" for Flip 2/4, and \"[F3/6]\" for Flip 3/6.\nType 'done' when you've finialized your selection.\nYou may also type 'last' to select your last chosen side deck."
            user = self.client.get_user(self.player1.id)
            await user.send(content=content, embed=self.game.showCardOptions(PLAYER_1))
            user = self.client.get_user(self.player2.id)
            await user.send(content=content, embed=self.game.showCardOptions(PLAYER_2))

   @commands.command()
   async def decline (self, ctx):
      if ctx.message.author.id != self.player2.id:
         await ctx.send(f"{ctx.message.author.mention}, you can't decline the challenge for {self.player2.mention}.")
      else:
         await ctx.send(f"{self.player1.mention}, {self.player2.mention} has declined the challenge. Please make another challenge by typing !pazaak and tagging your opponent.")
         self.game = None
         self.player1 = None
         self.player2 = None

   @commands.Cog.listener()
   async def on_message (self, message):
      if isinstance(message.channel, discord.channel.DMChannel) and message.author.id != config['bot_id'] and (message.author.id == self.player1.id or message.author.id == self.player2.id) and not self.finishedSelection:
         cardOptions = ["[+1]", "[+2]", "[+3]", "[+4]", "[+5]", "[+6]", "[-1]", "[-2]", "[-3]", "[-4]", "[-5]", "[-6]", "[+/-1]", "[+/-2]", "[+/-3]", "[+/-4]", "[+/-5]", "[+/-6]", "[F2/4]", "[F3/6]", "[D]", "[T]"]
         action = ""

         if message.content == "done" or message.content == "last":
            action = message.content
         else:
            try:
               action, card, amount = message.content.split(' ')
            except:
               try:
                  action, card = message.content.split(' ')
                  amount = 1
               except:
                  await message.channel.send("Your input was invalid. Please try again.")

         if action == "done" or action == "last" or (card in cardOptions and (action == "add" or action == "remove")):
            if message.author.id == self.player1.id and not self.game.finishedSelection(PLAYER_1):
               currentPlayer = PLAYER_1
            if message.author.id == self.player2.id and not self.game.finishedSelection(PLAYER_2):
               currentPlayer = PLAYER_2
            
            if action == "done":
               if self.game.completedSideDeck(currentPlayer):
                  self.game.finishSelection(currentPlayer)
                  await message.channel.send(embed=self.game.showPlayableCards(currentPlayer))
               else:
                  await message.channel.send("You need to select 10 cards before moving on.")
            
            if action == "last":
               db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
               cursor = db.cursor()

               try:
                  cursor.execute(f"SELECT plus_one, plus_two, plus_three, plus_four, plus_five, plus_six, minus_one, minus_two, minus_three, minus_four, minus_five, minus_six, plus_minus_one, plus_minus_two, plus_minus_three, plus_minus_four, plus_minus_five, plus_minus_six, flip_two_four, flip_three_six, double_card, tiebreaker_card FROM pazaak_last_deck WHERE discordid = {message.author.id}")
                  lastDeck = cursor.fetchone()

                  for i in range(len(cardOptions)):
                     cardOption = cardOptions[i].translate({ord(n): None for n in '[]'})

                     for j in range(lastDeck[i]):
                        self.game.makeSelection(currentPlayer, cardOption, "add")
               except Exception as e:
                  print(str(e))

               db.close()

            if action == "add":
               card = card.translate({ord(i): None for i in '[]'})
               amount = int(amount)

               if self.game.canAddCards(currentPlayer, card, amount):
                  for i in range(amount):
                     self.game.makeSelection(currentPlayer, card, action)
               else:
                  await message.channel.send(f"You don't currently own {self.game.getTotalSelected(card)} [{card}] cards. Please enter the right card and amount that you currently own that you would like to add.")
                  
            if action == "remove":
               card = card.translate({ord(i): None for i in '[]'})
               amount = int(amount)

               if self.game.canRemoveCards(currentPlayer, card, amount):
                  for i in range(amount):
                     self.game.makeSelection(currentPlayer, card, action)
               else:
                  await message.channel.send(f"You only have {self.game.getCurrentSelected(card)} [{card}] cards selected. Please enter the right card and amount that you currently have selected that you would like to remove.")
            
            if action != "done":
               await message.channel.send(embed=self.game.showSelection(currentPlayer))

            if self.game.finishedSelection(PLAYER_1) and self.game.finishedSelection(PLAYER_2):
               self.finishedSelection = True
               await self.client.get_channel(847627259275116554).send(f"{self.player1.mention}, please type !heads or !tails for the coin toss to see who will start the first round.")
         else:
            await message.channel.send("Your input was invalid. Please try again.")

   @commands.command()
   async def heads (self, ctx):
      if ctx.message.author.id == self.player1.id:
         await ctx.send(self.game.coinToss("heads"))
         self.game.setCard(randint(1,10))
         await ctx.send(content=self.content, embed=self.game.displayBoard())
      else:
         await ctx.send(f"{ctx.message.author.mention}, you can't play for {self.player1.mention}.")

   @commands.command()
   async def tails (self, ctx):
      if ctx.message.author.id == self.player1.id:
         await ctx.send(self.game.coinToss("tails"))
         self.game.setCard(randint(1,10))
         await ctx.send(content=self.content, embed=self.game.displayBoard())
      else:
         await ctx.send(f"{ctx.message.author.mention}, you can't play for {self.player1.mention}.")

   @commands.command()
   async def end (self, ctx):
      if ctx.message.author.id == self.game.getCurrentPlayerID():
         self.cardPlayed = False
         self.game.endTurn()
         if await turnEnd(self, ctx):
            await ctx.send(embed=self.game.displayBoard())
      else:
         await ctx.send(f"{ctx.message.author.mention}, you can't play for {self.game.mentionCurrentPlayer()}.")

   @commands.command()
   async def stand (self, ctx):
      if ctx.message.author.id == self.game.getCurrentPlayerID():
         self.cardPlayed = False
         self.game.stand()
         if await turnEnd(self, ctx):
            await ctx.send(embed=self.game.displayBoard())
      else:
         await ctx.send(f"{ctx.message.author.mention}, you can't play for {self.game.mentionCurrentPlayer()}.")

   @commands.command()
   async def play (self, ctx, card, sign=None):
      if ctx.message.author.id == self.game.getCurrentPlayerID():
         card = card.translate({ord(i): None for i in '[]'})
         if self.cardPlayed:
            await ctx.send("You already played a card this turn. Type !end to end your turn or !stand to stay on your hand.")
         elif not self.game.canPlayCard(card):
            await ctx.send(f"You don't have a [{card}] card in your side deck.")
         else:
            try:
               if card == "T":
                  self.game.setCard(int(f"{sign}1"), True, card)
               elif card == "D" or card == "F2/4" or card == "F3/6":
                  self.game.setCard(0, True, card)
               else:
                  if sign is None:
                     self.game.setCard(int(card), True, card)
                  else:
                     value = [int(i) for i in card if i.isdigit()][0]
                     self.game.setCard(int(f"{sign}{value}"), True, card)

               self.cardPlayed = True
               user = self.client.get_user(self.game.players[self.game.currentPlayer].id)
               if self.game.hasCardsLeft(self.game.currentPlayer):
                  await user.send(embed=self.game.showCurrentCards(self.game.currentPlayer))

            except Exception as e:
               print(str(e))
               await ctx.send("There was a mistake in your play input. Please try again using the proper formatting.")

            if await turnEnd(self, ctx):
               await ctx.send(embed=self.game.displayBoard())
      else:
         await ctx.send(f"{ctx.message.author.mention}, you can't play for {self.game.mentionCurrentPlayer()}.")

async def turnEnd (pazaak, ctx):
   if pazaak.game.turnOver():
      pazaak.game.stand()
      pazaak.cardPlayed = False
   if pazaak.game.roundOver():
      pazaak.game.findRoundWinner()
      if pazaak.game.roundWinner != TIED:
         await ctx.send(content=pazaak.game.declareRoundWinner(), embed=pazaak.game.displayBoard())
         if pazaak.game.gameOver():
            await ctx.send(pazaak.game.declareGameWinner())
            pazaak.game = None
            return False
      else:
         await ctx.send(content="Round tied!", embed=pazaak.game.displayBoard())
      await ctx.send(pazaak.game.nextRound())
   elif not pazaak.cardPlayed:
      pazaak.game.setCard(randint(1,10))
      if pazaak.game.turnOver():
         pazaak.game.stand()
         pazaak.cardPlayed = False
         await ctx.send(embed=pazaak.game.displayBoard())

   return True

def setup (client):
   client.add_cog(Pazaak(client))