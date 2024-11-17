import os
import discord
from discord import app_commands
import asyncio
import random
from discord.ext import commands
from discord.utils import get
import datetime
from datetime import timedelta
import json
from dotenv import load_dotenv
import constants
import aiosqlite

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")
APPLICATIONID: str = os.getenv("APPLICATIONID")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, application_id=APPLICATIONID)
async def init_db():
    async with aiosqlite.connect('profiles.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS profiles(
                         guild_id INTEGER NOT NULL,
                         user_id INTEGER NOT NULL,
                         charactername TEXT NOT NULL,
                         age INTEGER NOT NULL,
                         gender TEXT NOT NULL,
                         difficulty TEXT NOT NULL,
                         height TEXT NOT NULL,
                         cash INTEGER NOT NULL,
                         bank INTEGER NOT NULL,
                         attributes TEXT NOT NULL,
                         occupation TEXT NOT NULL,
                         moneylastcollected TEXT NOT NULL,
                         items TEXT NOT NULL,
                         PRIMARY KEY (guild_id, user_id)
                         )
                         ''')
        await db.commit()

async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py') and filename != "__init__.py":
            await bot.load_extension(f'cogs.{filename[:-3]}')
            await asyncio.sleep(1)

async def main():
    await load()
    await init_db()
    print("Starting")
    await asyncio.sleep(1)
    await bot.start(TOKEN)

@bot.event
async def on_ready():
    latency = round(bot.latency * 1000)
    print(f"Main ready! The ping is {latency}ms!")


@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx) -> None:
    print("Syncing")
    try:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f'Synced {len(fmt)} command(s)',)  
    except Exception as e:
        print(f"Unexpected Error: {e}")  

@bot.command()
async def bottest(ctx, *, arg):
    await ctx.send(arg)   

@bot.event
async def on_message(message):
    guild_id = message.guild.id
    print(f'Guild: {guild_id} | Message from {message.author}: {message.content}') 
    await bot.process_commands(message)


asyncio.run(main())