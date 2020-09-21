import shutil

# 3rd-party
import discord
from discord.ext import commands

import filepaths


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def wipe(self, ctx, *text_channels: discord.TextChannel):
        """Wipes all messages on the server"""

        # Console logging
        print(f'Wiping messages from server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            await text_channel.purge(limit=None)

        # Console logging
        print(f'Wiped messages from server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

    @commands.command()
    async def download(self, ctx):
        """Gets all messages from a guild and writes to txt"""

        await ctx.send("Downloading...")
        # make folder for messages
        message_dir = filepaths.WHITE_RABBIT_DIR / ctx.guild.name
        message_dir.mkdir(parents=True, exist_ok=True)

        # Download messages
        for channel in ctx.guild.text_channels:
            messages = [
                f"{message.created_at.strftime('%m/%d/%y %H:%M')} {message.author.display_name}: {message.clean_content}"
                async for message in channel.history(limit=None, oldest_first=True)
            ]
            with open(message_dir / f"{channel.name}.txt", mode="w") as message_file:
                message_file.write("\n".join(messages))

        # Send zip
        zip_file = filepaths.WHITE_RABBIT_DIR / f"{ctx.guild.name} Messages.zip"
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
