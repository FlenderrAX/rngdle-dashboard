import asyncio

import discord
from discord.ext import commands
import aiohttp
import datetime
import json
import os
import pathlib
from collections import Counter

class ProfileCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.server_avg_cache = {}

    async def fetch_basic_avg(self, session, rngdle_username):
        url = f"https://www.rngdle.com/api/users/{rngdle_username}/rolls"
        try:
            async with session.get(url) as response:
                if response.status != 200: return rngdle_username, 0
                api_data = await response.json()
                rolls = api_data.get("rolls", [])
                if not rolls: return rngdle_username, 0

                total = sum(r.get("totalScore", 0) for r in rolls if r)
                return rngdle_username, int(total / len(rolls))
        except:
            return rngdle_username, 0

    @discord.slash_command(name="profil")
    async def profil(
        self,
        ctx: discord.ApplicationContext,
        target: discord.Option(str, "RNGdle username or @mention a Discord user", required=False) = None
    ):
        await ctx.defer()

        guild_id = str(ctx.guild_id)

        script_path = pathlib.Path(__file__).resolve()
        local_save = os.path.join(script_path.parent.parent, "players.json")

        try:
            with open(local_save, "r") as f:
                data = json.load(f)
        except: data = {}

        rngdle_username = None

        if not target:
            if guild_id in data and str(ctx.author.id) in data[guild_id]:
                rngdle_username = data[guild_id][str(ctx.author.id)]
            else:
                await ctx.followup.send("You haven't linked an account yet! User `/register {username}` to link your account.", ephemeral=True)
                return
        elif target.startswith("<@") and target.endswith(">"):
            target_id = target.strip("<@!>")
            if guild_id in data and target_id in data[guild_id]:
                rngdle_username = data[guild_id][target_id]
            else:
                await ctx.followup.send("This user hasn't linked an RNGdle account!", ephemeral=True)
                return
        else:
            rngdle_username = target

        
        url = f"https://www.rngdle.com/api/users/{rngdle_username}/rolls"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.followup.send(f"Could not find the user {rngdle_username}!", ephemeral=True)
                        return
                    
                    api_data = await response.json()

                    if not api_data:
                        await ctx.followup.send(f"No rolls found for {rngdle_username}!", ephemeral=True)
                        return

                    rolls = list(map(dict, list(api_data.values())[0]))

            except Exception as e:
                await ctx.followup.send("An error has occured!") 
                print(f"API Error : {e}")
                return
            
        if not rolls:
            await ctx.followup.send(f"`{rngdle_username}` hasn't rolled anything!", ephemeral=True)
            return
        
        total_rolls = len(rolls)
        highest_score = 0
        total_score_sum = 0
        max_badges = 0
        total_hearts = 0
        lucky_number = 0

        highest_date = None
        first_roll_date = None
        latest_roll_date = None

        all_badges = []

        for roll in rolls:
            if not roll: continue

            score= roll.get("totalScore", 0)
            badges = roll.get("badgeCount", 0)
            hearts = roll.get("heartCount", 0)
            num = roll.get("number", 0)
            rolled_at_str = roll.get("rolledAt")

            rolled_date = datetime.datetime.fromisoformat(rolled_at_str.replace("Z", "+00:00"))

            total_score_sum += score
            total_hearts += hearts

            if score > highest_score:
                highest_score = score
                highest_date = rolled_date
                lucky_number = num

            if badges > max_badges:
                max_badges = badges

            if first_roll_date is None or rolled_date < first_roll_date:
                first_roll_date = rolled_date
            if latest_roll_date is None or rolled_date > latest_roll_date:
                latest_roll_date = rolled_date

            avg_score = int(total_score_sum / total_rolls) if total_rolls > 0 else 0

            server_rank_text = ""
            server_users = data.get(guild_id, {})

            if rngdle_username in server_users.values() and len(server_users) > 1:
                current_time = discord.utils.utcnow()

                if guild_id in self.server_avg_cache and (current_time - self.server_avg_cache[guild_id]["timestamp"]).total_seconds() < 3600:
                    server_averages = self.server_avg_cache[guild_id]["averages"]
                else:
                    async with aiohttp.ClientSession() as session:
                        tasks = [self.fetch_basic_avg(session, uname) for uname in server_users.values()]
                        results = await asyncio.gather(*tasks)

                    server_averages = sorted(results, key=lambda x: x[1], reverse=True)
                    self.server_avg_cache[guild_id] = {
                        "timestamp": current_time,
                        "averages": server_averages
                    }
                
                rank = 0
                for index, (uname, avg) in enumerate(server_averages, start=1):
                    if uname.lower() == rngdle_username.lower():
                        rank = index
                        break

                if rank > 0:
                    server_rank_text = f"\n(Server Rank: #{rank})"

        embed = discord.Embed(
            title=f"RNGdle Profile : {rngdle_username}",
            color = discord.Color.gold()
        )

        embed.add_field(name="🎲 Total Rolls", value=f"**{total_rolls}** rolls\n\u200b", inline=True)
        embed.add_field(name="📈 Average Score", value=f"**{avg_score:,}** EP".replace(",", " ") + f"{server_rank_text}\n\u200b", inline=True)
        embed.add_field(name="♥️ Total Hearts", value=f"**{total_hearts}** hearts\n\u200b", inline=True)

        if highest_date:
            highest_str = f"**{highest_score:,}** EP".replace(",", " ")
            embed.add_field(
                name="🏆 Highest Score",
                value=f"{highest_str} *(<t:{int(highest_date.timestamp())}:D>)*\nLucky Seed : `{lucky_number:,}`\n\u200b".replace(",", " "),
                inline=False
            )

        embed.add_field(name="🎖️ Max Badges Record", value=f"**{max_badges}** badges in a single roll\n\u200b", inline=False)

        if first_roll_date and latest_roll_date:
            dates_str = f"**First roll:** <t:{int(first_roll_date.timestamp())}:R>\n**Last roll:** <t:{int(latest_roll_date.timestamp())}:R>"
            embed.add_field(name="📅 Timeline", value=dates_str, inline=False)

        linked_user_id = None
        if guild_id in data:
            for uid, uname in data[guild_id].items():
                if uname.lower() == rngdle_username.lower():
                    linked_user_id = uid
                    break
                    
        if linked_user_id:
            member = ctx.guild.get_member(int(linked_user_id))
            if member:
                embed.set_thumbnail(url=member.display_avatar.url)

        embed.set_footer(text="RNGdle Stats")
        embed.timestamp = discord.utils.utcnow()

        await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(ProfileCog(bot))