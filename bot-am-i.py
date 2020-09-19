import discord
from discord.ext import commands
import os, json

client = commands.Bot(command_prefix = '!')
client.remove_command('help')

with open('./cogs/config.json') as data:
   config = json.load(data)

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
   if filename.endswith('.py') and not('twitch' in filename):
      client.load_extension(f'cogs.{filename[:-3]}')

client.run(config['discord_token'])