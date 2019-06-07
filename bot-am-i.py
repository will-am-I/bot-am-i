import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix = '!')

@client.command()
async def load(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      client.load_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been loaded in')
   
@client.command()
async def unload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      client.unload_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been unloaded out')
   
@client.command()
async def reload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      client.unload_extension(f'cogs.{extension}')
      client.load_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been reloaded')
   
for filename in os.listdir('./cogs'):
   if filename.endswith('.py'):
      client.load_extension(f'cogs.{filename[:-3]}')

client.run('NTg1NTcxNjQyMzExMzExNDQ4.XPfmJA._XEhpGt2sss7rPLyOIzO8q1DHX4')