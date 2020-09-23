# Built-in
import asyncio
import shutil
from PIL import Image
# 3rd-party
import discord
from discord.ext import commands
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
# Local
import utils
import gamedata

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

    @commands.command()
    async def pdf(self, ctx):
        """Exports the game to a PDF"""

        FONT = "Times-Roman"

        def from_corner(x, y, top=True, left=True, pagesize=pagesizes.letter):
            """Converts distance from corner to cartesian coordinates"""
            return x if left else pagesize[0] - x, pagesize[1] - y if top else y

        def draw_image(filepath, coordinates, shrink=4):
            temp_png = utils.WHITE_RABBIT_DIR / f"temp {filepath.stem}.png"
            Image.open(filepath).reduce(shrink).save(temp_png)
            c.drawImage(temp_png, *coordinates)
            temp_png.unlink()

        c = canvas.Canvas(str(utils.WHITE_RABBIT_DIR / "test.pdf"), pagesize=pagesizes.letter)
        for character in gamedata.CHARACTERS:
            # character name
            c.setFont(FONT, 40)
            c.drawString(*from_corner(50, 50), gamedata.CHARACTERS[character].split()[0])
            c.drawString(*from_corner(50, 100), gamedata.CHARACTERS[character].split()[1])

            # character and motive card
            draw_image(utils.MASTER_PATHS[character], from_corner(200, 300))
            draw_image(
                utils.MOTIVE_DIR / f"Motive {ctx.game.motives[character]}.png",
                from_corner(400, 300)
            )

            c.showPage()
        c.save()


def setup(bot):
    bot.add_cog(Admin(bot))
