import discord
from discord.ext import commands

MODERATOR_ID = 585922177149304833

class Moderation(commands.Cog):

   def __init__ (self, client):
      self.client = client
   
   #Kick Member
   @commands.command()
   async def kick(self, ctx, member : discord.Member, *, reason=None):
      if ctx.message.author.role.id == MODERATOR_ID:
         await ctx.send(f'{member} kicked for {reason}')
         await member.kick(reason=reason)
   
   #Ban Member
   @commands.command()
   async def ban(self, ctx, member : discord.Member, *, reason=None):
      if ctx.message.author.role.id == MODERATOR_ID:
         await ctx.send(f'{member} banned for {reason}')
         await member.ban(reason=reason)
   
   #Unban Member
   @commands.command()
   async def unban(self, ctx, *, member):
      if ctx.message.author.role.id == MODERATOR_ID:
         banned_users = await ctx.guild.bans()
         member_name, member_discriminator = member.split('#')
         
         for ban_entry in banned_users:
            user = ban_entry.user
            
            if (user.name, user.discriminator) == (member_name, member_discriminator):
               await ctx.guild.unban(user)
               await ctx.send(f'{user.mention} unbanned')
               return
   
async def setup (client):
   print("Moderation loaded")
   await client.add_cog(Moderation(client))