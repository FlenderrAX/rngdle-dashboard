import discord
from discord.commands import slash_command
from discord.ext import commands
import json
import pathlib
import os

class Unregister(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @slash_command(name='unregister')
    async def unregister(
        self,
        ctx: discord.ApplicationContext,
        username: str
    ):  
        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = f"{parent_path}{os.sep}players.json"
        
        with open(local_save, "r") as f:
            data = json.load(f)
        
        if str(ctx.user.id) not in list(data.keys()): 
            await ctx.respond("You haven't registered your username yet!")
            return

        if username.lower() != data[str(ctx.user.id)]: 
            await ctx.respond(f"You cannot unregister another user!\nYour username `{data[str(ctx.user.id)]}`")
            return
        
        data.pop(str(ctx.user.id))

        with open(local_save, "w") as f:
            json.dump(data, f)

        await ctx.respond(data)
    


def setup(bot):
    bot.add_cog(Unregister(bot))