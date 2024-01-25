import discord, os, json, asyncio
from discord.ext import commands

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

with open('./cogs/config.json') as data:
   config = json.load(data)

#Load Cog
@client.command()
async def load(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.load_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been loaded')

#Unload Cog
@client.command()
async def unload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.unload_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been unloaded')

#Reload Cog
@client.command()
async def reload(ctx, extension):
   if ctx.message.author.id == 320246151196704768:
      await client.reload_extension(f'cogs.{extension}')
      await ctx.send(f'{extension} has been reloaded')

async def startup():
   for filename in os.listdir('./cogs'):
      if filename.endswith('.py'):
         await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
   async with client:
      await startup()
      await client.start(config['discord_token'])

asyncio.run(main())