from discord.ext import commands
from discord.utils import get

class Roles(commands.Cog):
   def __init__ (self, client):
      self.client = client

   @commands.Cog.listener()
   async def on_raw_reaction_add(self, payload):
      #Streamer
      stream_announcement = await self.client.get_channel(834261336971673611).fetch_message(834277475667673089)
      if payload.message_id == stream_announcement.id and payload.emoji.name == "💜":
         role = get(payload.member.guild.roles, id=834268329371631646)
         await payload.member.add_roles(role)

   @commands.Cog.listener()
   async def on_raw_reaction_remove(self, payload):
      # Streamer
      stream_announcement = await self.client.get_channel(834261336971673611).fetch_message(834277475667673089)
      #pokemon = await self.client.get_channel(834261336971673611).fetch_message()
      #pazaak = await self.client.get_channel(834261336971673611).fetch_message()
      if payload.message_id == stream_announcement.id and payload.emoji.name == "💜":
         guild = self.client.get_guild(payload.guild_id)
         member = guild.get_member(payload.user_id)
         role = get(guild.roles, id=834268329371631646)
         await member.remove_roles(role)
      #if payload.message_id == pokemon.id and payload.emoji.name == "":

   @commands.Cog.listener()
   async def on_message(self, message):
      if message.channel.id == 855615027549831189 and message.content == "p!start":
         role = get(message.guild.roles, id=669228505128501258)
         await message.author.add_roles(role)

def setup (client):
   client.add_cog(Roles(client))