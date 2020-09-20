# Built-in
import asyncio
import random
import time
from pathlib import Path
import typing
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import gamedata

CARD_DIR = Path("Images/Cards")
RESOURCE_DIR = Path("Images/Player Resources")
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"


class Game(commands.Cog):
    def __init__(self, bot):
        self.games = {}

    async def cog_before_invoke(self, ctx):
        ctx.game = self.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))
        ctx.text_channels = {
            channel.name: channel
            for channel in ctx.guild.text_channels
        }

    async def cog_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.UserInputError):
            await ctx.send("Invalid input")
        else:
            await ctx.send("There was an error")
        print(error)

    @commands.command()
    async def error(self, ctx, channel: discord.TextChannel):
        raise NotImplementedError("SDFSFFDSFSDASSDGDGSFVCBKSJBD")

    @commands.Cog.listener()
    async def on_ready(self):
        self.timer.start()

    @commands.command()
    async def setup(self, ctx):
        """Sends out cards and sets up the game"""
        def send_image(channel, filepath):
            if isinstance(channel, str):
                channel = ctx.text_channels[channel]
            asyncio.create_task(channel.send(
                file=discord.File(filepath)
            ))

        def send_folder(channel, path):
            for image in sorted(path.glob("*")):
                send_image(channel, image)

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return
        elif ctx.game.setup:
            await ctx.send("Setup already run!")
            return

        await ctx.send("Starting setup")

        # Introduction images
        send_image("player-resources", RESOURCE_DIR / "Alice is Missing - Guide.jpg")
        send_image("player-resources", RESOURCE_DIR / "Alice is Missing - Character Sheet.jpg")
        send_image("player-resources", CARD_DIR / "Misc" / "Introduction.png")
        alice = random.choice(list(Path("Images/Missing Person Posters").glob("*.png")))
        send_image("player-resources", alice)

        # Send characters, suspects, and locations to appropriate channels
        send_folder("character-cards", CHARACTER_IMAGE_DIR)
        send_folder("suspect-cards", SUSPECT_IMAGE_DIR)
        send_folder("location-cards", LOCATION_IMAGE_DIR)

        # Character and motive cards in clues channels
        for first_name, full_name in gamedata.CHARACTERS.items():
            channel = ctx.text_channels[f"{first_name}-clues"]
            send_image(channel, CHARACTER_IMAGE_DIR / f"{full_name}.png")
            if ctx.game.automatic:
                send_image(
                    channel,
                    CARD_DIR / "Motives" / f"Motive {ctx.game.motives[first_name]}.png"
                )

        # 90 minute card for Charlie Barnes
        channel = ctx.text_channels["charlie-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            "Images/Cards/Clues/90/90-1.png"
        )))
        first_message = "Hey! Sorry for the big group text, but I just got "\
                        "into town for winter break at my dad's and haven't "\
                        "been able to get ahold of Alice. Just wondering if "\
                        "any of you have spoken to her?"
        prompts = "\n".join([
            "Read introduction", "Introduce alice from poster",
            "Introduce/pick characters", "Explain character cards",
            "Explain drive cards", "Character introductions (relationships)",
            "Voicemails", "Suspects and locations", "Explain clue cards",
            "Explain searching", "game guide",
            "setup playlist https://www.youtube.com/watch?v=ysOOFIOAy7A",
            "Run !start", "90 min card",
        ])
        asyncio.create_task(channel.send(f"```{prompts}```"))
        asyncio.create_task(channel.send(first_message))

        ctx.game.setup = True

    @commands.command()
    async def shuffle_clues(self, ctx):
        """Randomizes and assigns clue times"""

        # Stop if fewer than 3 player roles assigned
        if len(ctx.game.char_roles()) < 3:
            await ctx.send("Not enough players!")
            return

        player_count = len(ctx.game.char_roles())
        acceptable = False
        while not acceptable:
            clue_buckets = self.randomize_clues(player_count)
            acceptable = self.test_clue_buckets(clue_buckets)
        
        # Give bucket with 90 minute card to Charlie Barnes
        for i in range(len(clue_buckets)):
            for time in clue_buckets[i]:
                if time == 90:
                    charlie_bucket = i # Willy Wonka sends his regards

        bucket_assignments = {}
        bucket_assignments["charlie"] = clue_buckets.pop(charlie_bucket)
        
        # Assign the rest of the buckets randomly
        names = list(ctx.game.char_roles().keys())
        names = [item.lower() for item in names]
        names.pop(0) # Need to remove charlie from list
        random.shuffle(clue_buckets)
        for name in names:
            bucket_assignments[name] = clue_buckets.pop()
        
        # Print in a code block
        message = "```"
        for player in bucket_assignments:
            bucket_assignments[player].sort(reverse=True)
            clues = player.title() + ": " + ", ".join(str(bucket_assignments[player][x]) for x in range(len(bucket_assignments[player]))) + "\n"
            message += clues
        
        message += "```"
        asyncio.create_task(ctx.send(message))

        # Console logging
        print("Randomly assigned clue cards!")
        print(bucket_assignments)
    
    def randomize_clues(self, player_count: int):
        shuffled_clues = list(gamedata.CLUE_TIMES)
        random.shuffle(shuffled_clues)
        clue_buckets = []
        for i in range(player_count):
            clue_buckets.append([])
        for i in range(len(gamedata.BUCKET_SIZES[player_count])):
            for _ in range(gamedata.BUCKET_SIZES[player_count][i]):
                clue_buckets[i].append(shuffled_clues.pop())

        return clue_buckets


    def test_clue_buckets(self, clue_buckets):
        """
        Checks to see if any clue bucket contains two times 
        within 10 minutes of each other
        """

        for bucket in range(len(clue_buckets)):
            for i in range(len(clue_buckets[bucket])):
                start = i+1
                end = len(clue_buckets[bucket])
                for j in range(start, end):
                    if abs(clue_buckets[bucket][i]-clue_buckets[bucket][j]) <= 10:
                        return False
        
        return True

    @commands.command()
    async def start(self, ctx):
        """Begins the game"""

        if not ctx.game.setup:
            await ctx.send("Can't start before setting up!")
            return

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        if len(ctx.game.char_roles()) < 3:
            await ctx.send("Not enough players!")
            return

        ctx.game.start_time = time.time()
        ctx.game.started = True
        await ctx.send("Starting the game!")

    @commands.command(name="timer")
    async def show_time(self, ctx):
        """Show/hide bot timer"""

        ctx.game.show_timer = not ctx.game.show_timer
        if ctx.game.show_timer:
            await ctx.send("Showing bot timer!")
        else:
            await ctx.send("Hiding bot timer!")

    @commands.command()
    async def automatic(self, ctx):
        """Enable/disable automatic mode"""

        ctx.game.automatic = not ctx.game.automatic
        await ctx.send(f"{'En' if ctx.game.automatic else 'Dis'}abling automatic card draw")

    @commands.command()
    async def draw_motive(self, ctx):
        character = self.get_char(ctx.author)
        if not character:
            await ctx.send("You don't have a character role")
            return
        channel = ctx.text_channels[f"{character}-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            CARD_DIR / "Motives" / f"Motive {ctx.game.motives[character]}.png"
        )))

    def get_char(self, member: discord.Member):
        for role in member.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                return role.name.lower()

    @tasks.loop(seconds=gamedata.TIMER_GAP)
    async def timer(self):
        for game in self.games.values():
            # Skip if game has not started
            if not game.started:
                continue
            # Skip if game has ended
            if game.start_time + gamedata.GAME_LENGTH < time.time():
                continue

            remaining_time = game.start_time + gamedata.GAME_LENGTH - time.time()

            if game.show_timer:
                text_channels = {
                    channel.name: channel
                    for channel in game.guild.text_channels
                }
                await text_channels["bot-channel"].send((
                    f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
                ))

    @commands.command()
    async def search(self, ctx):
        if not ctx.game.started:
            await ctx.send("The game hasn't started yet")
        character = self.get_char(ctx.author)
        if not character:
            await ctx.send("You don't have a character role")
            return

        search_card = random.choice((CARD_DIR / "Searching").glob("*.png"))
        asyncio.create_task(ctx.text_channels[f"{character}-clues"].send(
            file=discord.File(search_card)
        ))

    @commands.command(name="10")
    async def ten_min_card(self, ctx, character: typing.Union[discord.Member, discord.Role]):
        if isinstance(character, discord.Member):
            character = self.get_char(character)
            if not character:
                await ctx.send("Could not find character")
        ctx.game.ten_char = character.name.lower()
        # await ctx.text_channels[f"{character.name.lower()}-clues"].send(
        #     file=discord.File(random.choice(list((CLUE_DIR / "10").glob("10-*.png")))
        # ))


def setup(bot):
    bot.add_cog(Game(bot))
