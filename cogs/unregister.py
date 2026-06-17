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
        ctx: discord.ApplicationContext
    ):  
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = os.path.join(parent_path, "players.json")

        try:
            with open(local_save, "r") as f:
                data = json.load(f)
        except: data = {}
        
        if guild_id not in data or user_id not in data[guild_id]:
            await ctx.respond("You haven't registrated your account yet!", ephemeral=True)
            return

        removed_username = data[guild_id].pop(user_id)

        with open(local_save, "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title="Succesfully unregistrated !",
            description=f"You just dissociated your account : `{removed_username}`.",
            color=discord.Color.red()
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.set_footer(text="RNGdle Bot • Use /leaderboard to see the leaderboard")

        await ctx.respond(data)
    

def setup(bot):
    bot.add_cog(Unregister(bot))