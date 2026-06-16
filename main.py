import discord
import os
import json

from dotenv import load_dotenv
# import asyncio

def is_json_empty(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data == {} or data == [] or not data
    except json.JSONDecodeError:
        return True
    except FileNotFoundError:
        print("The specified file does not exist.")
        return True

load_dotenv()

TOKEN = os.getenv("RNGDLE_BOT")

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    filename = "players.json"
    if is_json_empty(filename):
        with open(filename, "w") as f: 
            json.dump({}, f)

    print(f'Logged as {bot.user} !')
    # while True:
    #     await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='A nice game'))
    #     await asyncio.sleep(60)


extensions = [
    'cogs.register',
    'cogs.unregister',
    'cogs.leaderboard'
]

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
        print(f"+ Cog loaded : {extension}")

bot.run(TOKEN)