import discord
import time
import random
import asyncio
from discord.ext import commands, tasks


class AliceIsMissing(commands.Cog):
    CHARACTERS = (
        "Charlie Barnes", "Dakota Travis",
        "Evan Holwell", "Jack Briarwood", "Julia North"
    )
    GAME_LENGTH = 90 * 60

    def __init__(self, bot):
        self.bot = bot
        self.setup = False

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.text_channels = {
            channel.name: channel
            for channel in self.bot.guilds[0].text_channels
        }
        print(f"Bot has logged in as {self.bot}")

    @commands.command()
    async def start(self, ctx):
        if not self.setup:
            await ctx.send("You have not setup")
            return
        self.start_time = time.time()
        self.timer.start()
        await ctx.send('Starting the game!')

    @tasks.loop(seconds=10)
    async def timer(self):
        if self.start_time + self.GAME_LENGTH < time.time():
            self.timer.cancel()

        remaining_time = self.start_time + self.GAME_LENGTH - time.time()
        await self.text_channels["group-chat"].send((
            f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
        ))

    @commands.command()
    async def setup(self, ctx):
        # Send character cards
        motives = list(range(1, 6))
        random.shuffle(motives)
        for motive, character in zip(motives, self.CHARACTERS):
            channel = self.text_channels[f"{character.lower().split()[0]}-clues"]
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Characters/{character.title()}.png"
            )))
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Motives/Motive {motive}.png"
            )))
        self.setup = True
        await ctx.send("Set up complete")

    @commands.command()
    async def claim(self, ctx, role: discord.Role):
        if role.name.title() not in [name.split()[0] for name in self.CHARACTERS]:
            await ctx.send("You cannot claim that role")
        elif role.members:
            await ctx.send("That role is taken")
        elif len(ctx.author.roles) > 1:
            await ctx.send(f"You already have {ctx.author.roles[-1].name}")
        else:
            await ctx.author.add_roles(role)
            await ctx.send(f"Gave you {role.name}!")

    @commands.command()
    async def unclaim(self, ctx):
        # keep @everyone
        await ctx.author.edit(roles=[ctx.author.roles[0]])
        await ctx.send("Removed all roles")


def setup(bot):
    bot.add_cog(AliceIsMissing(bot))
