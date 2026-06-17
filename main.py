import discord
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("RNGDLE_BOT")

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    filename = "players.json"
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        with open(filename, "w") as f:
            json.dump({}, f)
    print(f"Logged in as {bot.user} !")

extensions = [
    'cogs.register',
    'cogs.unregister',
    'cogs.leaderboard'
]

for ext in extensions:
    bot.load_extension(ext)
    print(f"+ Cogs loaded : {ext}.py")

bot.run(TOKEN)