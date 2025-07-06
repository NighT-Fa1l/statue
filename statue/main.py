import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="oy statue ", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def main():
    async with bot:
        for filename in os.listdir("./commands"):
            if filename.endswith(".py") and filename not in ("spotify_client.py", "__init__.py"):
                await bot.load_extension(f"commands.{filename[:-3]}")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
