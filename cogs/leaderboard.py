import discord
import pathlib
import json
import os
import datetime
import aiohttp
import asyncio

from discord.ext import commands

class LeaderboarCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
        self.cache = {}

    
    leaderboard = discord.SlashCommandGroup(
        name="leaderboard",
        description="All commands related to server leaderboards"
    )

    async def fetch_user_score(self, session, discord_user_id, rngdle_username):
        url = f"https://www.rngdle.com/api/users/{rngdle_username}/rolls"

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()

                if not data:
                    return None
                
                rolls = list(map(dict, list(data.values())[0]))

                current_date = datetime.date.today().strftime("%d/%B/%Y")

                for roll in rolls:
                    if not roll: continue
                    rolled_date = datetime.datetime.fromisoformat(roll["rolledAt"]).strftime("%d/%B/%Y")

                    if current_date == rolled_date:
                        return (discord_user_id, rngdle_username, roll["totalScore"])
                    
        except Exception as e:
            print(f"API Error :{e}")

        return None
    
    @leaderboard.command(name="show")
    async def show(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        guild_id = str(ctx.guild.id)
        current_time = discord.utils.utcnow()

        if guild_id in self.cache:
            time_diff = current_time - self.cache[guild_id]["timestamp"]
            if time_diff.total_seconds() < 600:
                await self.send_leaderboard(ctx, self.cache[guild_id]["scores"], self.cache[guild_id]["timestamp"])
                return
            
        script_path = pathlib.Path(__file__).resolve()
        parent_path = script_path.parent.parent
        local_save = os.path.join(parent_path, "players.json")

        try:
            with open(local_save, "r") as f:
                data = json.load(f)
        except:
            data = {}

        if guild_id not in data or not data[guild_id]:
            await ctx.respond("No player is registrated on this server!")
            return
        
        users = data[guild_id]

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_user_score(session, uid, uname) for uid, uname in users.items()]
            results = await asyncio.gather(*tasks)

        scores = [res for res in results if res is not None]
        scores.sort(key=lambda x: x[2], reverse=True)

        self.cache[guild_id] = {
            "timestamp": current_time,
            "scores": scores
        } 

        await self.send_leaderboard(ctx, scores, current_time)

    async def send_leaderboard(self, ctx, scores, fetch_time):
        if not scores:
            leaderboard_text = "*No score today!*"
        else:
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            leaderboard_text = "```text\n"
            leaderboard_text += f"{'Rank':<4} | {'Player':<16} | {'Score':<11}\n"
            leaderboard_text += "-" * 37 + "\n"

            for index, (uid, uname, score) in enumerate(scores[:10], start=1):
                member = ctx.guild.get_member(int(uid))
                display_name = (member.display_name if member else uname)[:16]

                if index in medals:
                    rank_str = f"{medals[index]}"
                else:
                    rank_str = f"#{index:<2}"
            
                leaderboard_text += f"{rank_str} | {display_name:<16} | {score:>7,} EP\n"

            leaderboard_text += "```"

        embed = discord.Embed(
            title=f"{ctx.guild.name} RNGdle Leaderboard",
            description=leaderboard_text,
            color=discord.Color.gold()
        )

        embed.set_footer(text="Last data refresh")
        embed.timestamp = fetch_time

        await ctx.followup.send(embed=embed)

    @leaderboard.command(default_member_permissions=discord.Permissions(administrator=True))
    async def refresh(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        if guild_id in self.cache:
            del self.cache[guild_id]

        await ctx.respond("Data suppressed for this server!", ephemeral=True)

def setup(bot):
    bot.add_cog(LeaderboarCog(bot))