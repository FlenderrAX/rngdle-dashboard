import discord
from discord.commands import slash_command
from discord.ext import commands
import json
import pathlib
import os

class Register(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @slash_command(name='register')
    async def register(
        self,
        ctx: discord.ApplicationContext,
        username: str
    ):  
        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = f"{parent_path}{os.sep}players.json"

        with open(local_save, "r") as file:
            usernames = json.load(file)

            if str(ctx.user.id) in list(usernames.keys()): await ctx.respond("Already registrated"); return

            usernames[ctx.user.id] = username.lower()

        with open(local_save, "w") as file:
            json.dump(usernames, file)

        await ctx.respond(f"Added {username}")

def setup(bot):
    bot.add_cog(Register(bot))