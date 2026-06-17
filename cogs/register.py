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
        rngdle_username: str
    ):  
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = os.path.join(parent_path, "players.json")

        try:
            with open(local_save, "r") as file:
                data = json.load(file)
        except: data = {}
        
        if guild_id not in data:
            data[guild_id] = {}

        if user_id in data[guild_id]:
            await ctx.respond("You're already registrated ! Use `/unregister` command first.", ephemeral=True)
            return

        if rngdle_username in data[guild_id].values():
            await ctx.respond(f"The following account `{rngdle_username}` is already linked with another account!", ephemeral=True)
            return

        data[guild_id][user_id] = rngdle_username

        with open(local_save, "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title="Succesfully registrated !",
            description=f"You just linked your account to : `{rngdle_username}`.",
            color=discord.Color.green()
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.set_footer(text="RNGdle Bot • Use /leaderboard to see the leaderboard")

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Register(bot))