import discord, os, json, asyncio
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix = '!', intents=intents)
client.remove_command('help')

with open('./cogs/config.json') as data:
   config = json.load(data)

"""
@client.command()
async def load(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.load_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been loaded in')
   
@client.command()
async def unload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.unload_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been unloaded out')
   
@client.command()
async def reload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.unload_extension(f'cogs.{extension}')
      await client.load_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been reloaded')
"""
async def loadall(): 
   for filename in os.listdir('./cogs'):
      if filename.endswith('.py'):
         await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
   await loadall()
   await client.start(config['discord_token'])

asyncio.run(main())