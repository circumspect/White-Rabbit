# Built-in
import asyncio
import shutil
from PIL import Image
# 3rd-party
import discord
from discord.ext import commands
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
# Local
import gamedata
import utils

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command(aliases=["wipe"])
    async def reset(self, ctx, *text_channels: discord.TextChannel):
        """Resets server and game data"""

        # Confirm command to user
        await ctx.send("Resetting the server!")

        # Console logging
        print(f'Resetting server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            asyncio.create_task(text_channel.purge(limit=None))

        # Console logging
        print(f'Wiped messages from server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        # Reset game data
        ctx.game.__init__(ctx.game.guild)

    @commands.command()
    async def download(self, ctx):
        """Gets all messages from a guild and writes to a .txt file"""

        await ctx.send("Downloading...")
        # make folder for messages
        message_dir = utils.WHITE_RABBIT_DIR / ctx.guild.name
        message_dir.mkdir(parents=True, exist_ok=True)

        # Download messages
        for channel in ctx.guild.text_channels:
            messages = [
                " ".join((
                    message.created_at.strftime('%m/%d/%y %H:%M'),
                    message.author.display_name + ":",
                    message.clean_content,
                    ", ".join(attachment.url for attachment in message.attachments)
                ))
                async for message in channel.history(limit=None, oldest_first=True)
            ]
            with open(message_dir / f"{channel.name}.txt", mode="w") as message_file:
                message_file.write("\n".join(messages))

        # Send zip
        zip_file = utils.WHITE_RABBIT_DIR / f"{ctx.guild.name} Messages.zip"
        shutil.make_archive(
            zip_file.with_suffix(""),
            "zip", message_dir,
        )
        await ctx.send(file=discord.File(zip_file))

        # Delete files
        shutil.rmtree(message_dir)
        zip_file.unlink()

def setup(bot):
    bot.add_cog(Admin(bot))
