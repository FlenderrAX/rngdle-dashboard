import discord

from discord.ext import commands

import pathlib
import json
import os
import datetime
import requests

class LeaderboardCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.data = []

    leaderboard = discord.SlashCommandGroup(
        name="leaderboard", 
        description="All commands related to server leaderboards"
    )

    def get_rolls(self, user):
        url = f"https://www.rngdle.com/api/users/{user}/rolls"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

        rolls = list(map(dict, list(data.values())[0]))

        return rolls

    @leaderboard.command(name="show", description="Show the current leaderboard")
    async def show(self, ctx: discord.ApplicationContext):
        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = f"{parent_path}{os.sep}players.json"
        
        with open(local_save, "r+") as f:
            usernames = list(json.load(f).values())
        
        userscores = {}

        for user in usernames:
            for roll in self.get_rolls(user):

                if not roll: continue

                rolled_date = datetime.datetime.fromisoformat(roll["rolledAt"]).strftime("%d/%B/%Y")
                current_date = datetime.date.today().strftime("%d/%B/%Y")

                if current_date == rolled_date:
                    todays_roll = roll
                    userscores[user] = todays_roll["totalScore"]
                    continue
        
        sorted_scores = sorted([(user, score) for user, score in userscores.items()], key=lambda x: x[1])

        leaderboard_text = ""

        for index, (user, score) in enumerate(sorted_scores[:10], start=1):
            leaderboard_text += f"**{index} - {user}** — {score:,} pts\n"

        if not leaderboard_text:
            leaderboard_text = "No scores recorded yet!"

        embed = discord.Embed(
            title="🏆 SERVER LEADERBOARD 🏆",
            description=leaderboard_text,
            color=discord.Color.gold()
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/v8879bA.png")
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.respond(embed=embed)
    

    @leaderboard.command(description="Force refresh the leaderboard data")
    async def refresh(self, ctx: discord.ApplicationContext):
        await ctx.respond("Leaderboard data successfully refreshed!")

def setup(bot: discord.Bot):
    bot.add_cog(LeaderboardCog(bot))