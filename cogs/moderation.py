import discord
from discord.ext import commands

class Moderation(commands.Cog):
   
   MODERATOR_ID = ''
   
   def __init__ (self, client):
      self.client = client
   
   @commands.command()
   async def test(self, ctx):
      time = '26:54'
      link = 'https://www.speedrun.com/yl/run/zp05nr8m'
      game = 'Yooka-Laylee'
      place = '12th'
      cover = 'https://www.speedrun.com/themes/yl/cover-256.png'
      verified_date = 'Mar 2, 2019 at 11:50 pm'
      
      embed=discord.Embed(title=f'New Personal Best at {time}!', url=link, description=f'Will has set a new PB in {game} and is now {place} on the leaderboard.', color=0x55c5c6)
      embed.set_author(name='will-am-I', icon_url='https://www.speedrun.com/themes/user/will_am_I/image.png')
      embed.set_thumbnail(url=cover)
      embed.set_footer(text=f'Run verified {verified_date}.')
      await ctx.send(embed=embed)
   
   @commands.command()
   async def kick(self, ctx, member : discord.Member, *, reason=None):
      ctx.send(f'{member} kicked for {reason}')
      await member.kick(reason=reason)
      
   @commands.command()
   async def ban(self, ctx, member : discord.Member, *, reason=None):
      ctx.send(f'{member} banned for {reason}')
      await member.ban(reason=reason)
   
   @commands.command()
   async def unban(ctx, *, member):
      banned_users = await ctx.guild.bans()
      member_name, member_discriminator = member.split('#')
      
      for ban_entry in banned_users:
         user = ban_entry.user
         
         if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} unbanned')
            return
   
def setup (client):
   client.add_cog(Moderation(client))