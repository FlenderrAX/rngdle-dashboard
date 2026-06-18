import discord
from discord.ext import commands
import pathlib
import json
import os
import datetime
import aiohttp
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass

@dataclass
class LeaderboardUser:
    user: discord.User
    score: int
    rank: int


class LeaderboardGenerator:
    PODIUM_BRONZE: Image.Image
    PODIUM_SILVER: Image.Image
    PODIUM_GOLD: Image.Image

    WIDTH: int = 800
    ROW_HEIGHT: int = 90
    HEADER_HEIGHT: int = 100

    BG_COLOR = (25, 25, 25)
    TEXT_COLOR = (255, 255, 255)
    HEADER_BG_COLOR = (50, 50, 50)
    ROW_EVEN_COLOR = (35, 35, 35)
    ROW_ODD_COLOR = (45, 45, 45)
    HIGHLIGHT_COLOR = (0, 100, 200)

    def __init__(self):
        self.base_path = f"{pathlib.Path(__file__).parent.resolve()}/../ressources"
        self._load_static_resources()

    def _load_static_resources(self):
        try:
            self.PODIUM_BRONZE = Image.open(f"{self.base_path}/images/medal_bronze.png").convert("RGBA").resize((50, 50))
            self.PODIUM_SILVER = Image.open(f"{self.base_path}/images/medal_silver.png").convert("RGBA").resize((50, 50))
            self.PODIUM_GOLD = Image.open(f"{self.base_path}/images/medal_gold.png").convert("RGBA").resize((50, 50))
        except FileNotFoundError:
            print("Attention : Les images de médailles n'ont pas été trouvées dans le dossier ressources.")

        try:
            self.font_header = ImageFont.truetype(f"{self.base_path}/font/outfit.ttf", 40)
            self.font_regular = ImageFont.truetype(f"{self.base_path}/font/outfit.ttf", 30)
            self.font_small = ImageFont.truetype(f"{self.base_path}/font/outfit.ttf", 24)
        except IOError:
            print("Warning: Could not load specified font. Using Pillow's default font.")
            self.font_header = ImageFont.load_default()
            self.font_regular = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    async def generate_leaderboard(self, users: list[LeaderboardUser]):
        total_height = self.HEADER_HEIGHT + (len(users) * self.ROW_HEIGHT)
        img = Image.new("RGB", (self.WIDTH, total_height), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, self.WIDTH, self.HEADER_HEIGHT], fill=self.HEADER_BG_COLOR)

        headers = ["Rank", "Username", "Score"]
        x_offsets = [15, 190, 680]

        draw.text((x_offsets[0], self.HEADER_HEIGHT / 2 - 15), headers[0], fill=self.TEXT_COLOR, font=self.font_regular)
        draw.text((x_offsets[1], self.HEADER_HEIGHT / 2 - 15), headers[1], fill=self.TEXT_COLOR, font=self.font_regular)
        draw.text((x_offsets[2], self.HEADER_HEIGHT / 2 - 15), headers[2], fill=self.TEXT_COLOR, font=self.font_regular)

        for user in users:
            y_pos = self.HEADER_HEIGHT + ((user.rank - 1) * self.ROW_HEIGHT)
            row_color = self.ROW_EVEN_COLOR if (user.rank - 1) % 2 == 0 else self.ROW_ODD_COLOR
            draw.rectangle([0, y_pos, self.WIDTH, y_pos + self.ROW_HEIGHT], fill=row_color)

            rank_text_x = 30
            rank_text_y = y_pos + (self.ROW_HEIGHT / 2) - 15
            
            if user.rank == 1 and hasattr(self, 'PODIUM_GOLD'):
                try:
                    img.paste(self.PODIUM_GOLD, (rank_text_x - 15, int(rank_text_y - 10)), self.PODIUM_GOLD)
                except Exception:
                    draw.text((rank_text_x, rank_text_y), str(user.rank), fill=(255, 215, 0), font=self.font_regular)
            elif user.rank == 2 and hasattr(self, 'PODIUM_SILVER'):
                try:
                    img.paste(self.PODIUM_SILVER, (rank_text_x - 15, int(rank_text_y - 10)), self.PODIUM_SILVER)
                except Exception:
                    draw.text((rank_text_x, rank_text_y), str(user.rank), fill=(192, 192, 192), font=self.font_regular)
            elif user.rank == 3 and hasattr(self, 'PODIUM_BRONZE'):
                try:
                    img.paste(self.PODIUM_BRONZE, (rank_text_x - 15, int(rank_text_y - 10)), self.PODIUM_BRONZE)
                except Exception:
                    draw.text((rank_text_x, rank_text_y), str(user.rank), fill=(205, 127, 50), font=self.font_regular)
            else:
                draw.text((rank_text_x, rank_text_y), str(user.rank), fill=self.TEXT_COLOR, font=self.font_regular)

            avatar_x = 100
            avatar_y = int(y_pos + 15)
            avatar_size = 60
            try:
                avatar_data = await user.user.display_avatar.read()
                avatar_img = Image.open(BytesIO(avatar_data)).resize((avatar_size, avatar_size)).convert("RGBA")
                self.create_avatar_mask(avatar_img, avatar_size, avatar_x, avatar_y, img)
            except Exception:
                default_avatar = Image.new("RGBA", (avatar_size, avatar_size), (120, 120, 120, 255))
                self.create_avatar_mask(default_avatar, avatar_size, avatar_x, avatar_y, img)

            username_x = 190
            username_y = y_pos + (self.ROW_HEIGHT / 2) - 15
            
            display_name = user.user.display_name if isinstance(user.user, discord.Member) else user.user.name
            
            draw.text((username_x, username_y), display_name, fill=self.TEXT_COLOR, font=self.font_regular)

            score_x = 680
            score_y = y_pos + (self.ROW_HEIGHT / 2) - 15
            draw.text((score_x, score_y), f"{user.score:,}".replace(",", " "), fill=self.TEXT_COLOR, font=self.font_regular)

        return img

    @staticmethod
    def create_avatar_mask(avatar_img, avatar_size, avatar_x, avatar_y, img):
        mask = Image.new("L", (avatar_size * 4, avatar_size * 4), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, avatar_size * 4, avatar_size * 4), fill=255)
        mask = mask.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
        avatar_img.putalpha(mask)
        img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)


class LeaderboardCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.cache = {}
        self.generator = LeaderboardGenerator()

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

    @leaderboard.command(name="show", description="Show the current leaderboard")
    async def show(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        guild_id = str(ctx.guild.id)
        current_time = discord.utils.utcnow()

        if guild_id in self.cache:
            time_diff = current_time - self.cache[guild_id]["timestamp"]
            if time_diff.total_seconds() < 600:
                await self.send_leaderboard_image(ctx, self.cache[guild_id]["scores"], self.cache[guild_id]["timestamp"])
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

        await self.send_leaderboard_image(ctx, scores, current_time)

    async def send_leaderboard_image(self, ctx, scores, fetch_time):
        if not scores:
            await ctx.followup.send("*No score today!*")
            return
        
        lb_users = []
        for index, (uid, uname, score) in enumerate(scores[:10], start=1):
            member = ctx.guild.get_member(int(uid))
            
            if not member:
                member = type('MockUser', (object,), {'name': uname, 'display_avatar': ctx.bot.user.display_avatar})()

            lb_user = LeaderboardUser(user=member, score=score, rank=index)
            lb_users.append(lb_user)

        img = await self.generator.generate_leaderboard(lb_users)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(buffer, filename="leaderboard.png")

        await ctx.followup.send(
            file=file
        )

    @leaderboard.command(default_member_permissions=discord.Permissions(administrator=True))

    async def refresh(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        if guild_id in self.cache:
            del self.cache[guild_id]
        await ctx.respond("Data suppressed for this server!", ephemeral=True)

def setup(bot):
    bot.add_cog(LeaderboardCog(bot))