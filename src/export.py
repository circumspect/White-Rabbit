# Built-in
import asyncio
import datetime
import itertools
import math
from pathlib import Path
import shutil
from urllib.parse import urlparse
# 3rd-party
import discord
from discord.ext import commands
from fpdf import FPDF
# Local
import gamedata
import utils

# PDF export constants - all measurements are in inches
# Letter size paper
PAGE_WIDTH = 8.5 
PAGE_HEIGHT = 11
CARD_RATIO = 1057 / 757  # Card height to width ratio
AUTO_BREAK = 1

# Separator
BREAK_SEPARATOR_GAP = 0.1
SEPARATOR_THICKNESS = 0.01
WATERMARK_SEPARATOR_Y = PAGE_HEIGHT - AUTO_BREAK + BREAK_SEPARATOR_GAP
WATERMARK_SEPARATOR_LEFT = 0.45
WATERMARK_SEPARATOR_LENGTH = 3
WATERMARK_SEPARATOR_RIGHT = WATERMARK_SEPARATOR_LEFT + WATERMARK_SEPARATOR_LENGTH

# Watermark
SEPARATOR_WATERMARK_GAP = 0.1
WATERMARK_GAPS = (SEPARATOR_WATERMARK_GAP, 0.2)
WATERMARK = ("Created by:", "The White Rabbit")
WATERMARK_Y = WATERMARK_SEPARATOR_Y + SEPARATOR_WATERMARK_GAP

# Page numbers
PAGE_NUMBER_X = 8.2


# Cover page
COVER_TITLE_Y = 1
COVER_TITLE_POSTER_GAP = 0.8
COVER_POSTER_WIDTH = 6
COVER_POSTER_Y = COVER_TITLE_Y + COVER_TITLE_POSTER_GAP
COVER_POSTER_X = PAGE_WIDTH/2 - COVER_POSTER_WIDTH/2


# Character Pages
# Title cell size - if this is too small,
# the text will overlap itself
CHAR_TITLE_HEIGHT = 0.8
# Character/motive cards
# Dimensions of character/motive card images
CHAR_CARD_WIDTH = 2
CHAR_CARD_HEIGHT = CHAR_CARD_WIDTH * CARD_RATIO
# Character page title location
CHAR_TITLE_X = 0.7
CHAR_TITLE_Y = 0.5
# Character card location
CHAR_CARD_LEFT = 0.8
CHAR_TITLE_CARD_GAP = 0.3
CHAR_CARD_TOP = CHAR_TITLE_Y + CHAR_TITLE_HEIGHT * 2 + CHAR_TITLE_CARD_GAP
# Motive card location
CHAR_CARD_MOTIVE_GAP = 0.4
MOTIVE_CARD_TOP = CHAR_CARD_TOP + CHAR_CARD_HEIGHT + CHAR_CARD_MOTIVE_GAP

# Clues
# Card dimensions
CLUE_CARD_HEIGHT = 2.3
CLUE_CARD_WIDTH = CLUE_CARD_HEIGHT / CARD_RATIO
# Location
CLUE_CARD_LEFT = 4.5
CLUE_CARDS_TOP = 0.6
# Label positioning
CLUE_LABEL_CARD_GAP = 0.8
CLUE_LABEL_Y_OFFSET = 0.4
CLUE_LABEL_X = CLUE_CARD_LEFT - CLUE_LABEL_CARD_GAP
# Suspect card positioning
CLUE_SUSPECT_GAP = 0.3
SUSPECT_CARD_LEFT = CLUE_CARD_LEFT + CLUE_CARD_WIDTH + CLUE_SUSPECT_GAP
# Vertical gap between clues
CLUE_CLUE_GAP = 0.3


# Group chat/PM pages
MESSAGES_TITLE_Y = 0.5
MESSAGES_TITLE_TEXT_GAP = 0.3
MESSAGES_LINE_HEIGHT = 0.25


# Fonts
# Cover page
COVER_TITLE_FONT = ("Built", 'bd', 80)

# Character pages
CHAR_TITLE_FONT = ("Built", 'sb', 60)
CLUE_LABEL_FONT = ("Built", 'sb', 48)

# Message pages
PM_TITLE_FONT = ("Built", 'sb', 24)
PM_FONT = ("Baloo", '', 12)

# Footer
WATERMARK_FONTS = (("Baloo", '', 12), ("Baloo", '', 16))
PAGE_NUMBER_FONT = WATERMARK_FONTS[1]


# Font paths
FONT_DIR = utils.RESOURCE_DIR / "Fonts"

BALOO_DIR = FONT_DIR / "Baloo_Tammudu_2"
BALOO_REGULAR = BALOO_DIR / "BalooTammudu2-Regular.ttf"

BUILT_DIR = FONT_DIR / "built_titling"
BUILT_TITLING_SB = BUILT_DIR / "built titling sb.ttf"
BUILT_TITLING_BD = BUILT_DIR / "built titling bd.ttf"


class PDF(FPDF):
    # Page footer
    def footer(self):
        # Watermark separator
        self.set_line_width(SEPARATOR_THICKNESS)
        self.line(WATERMARK_SEPARATOR_LEFT, WATERMARK_SEPARATOR_Y, WATERMARK_SEPARATOR_RIGHT, WATERMARK_SEPARATOR_Y)

        self.set_y(WATERMARK_Y)
        # Watermark
        for i in range(len(WATERMARK)):
            self.set_y(self.get_y() + WATERMARK_GAPS[i])
            self.set_font(*WATERMARK_FONTS[i])
            text = WATERMARK[i]
            width = self.get_string_width(text)
            self.cell(width, 0, text, 0, 0, 'L')

        # Page number
        self.set_font(*PAGE_NUMBER_FONT)
        page_number_text = str(self.page_no() - 1)

        # Skip cover page
        if page_number_text != "0":
            self.cell(0, 0, page_number_text, 0, 0, 'R')


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def import_data(self, ctx):
        """imports data from message history"""

        # Find game start
        channel = ctx.text_channels["bot-channel"]
        async for message in channel.history(limit=None, oldest_first=True):
            if "!start" in message.content:
                ctx.game.start_time = message.created_at
                break

        # Alice
        channel = ctx.text_channels["player-resources"]
        image_list = list(itertools.chain.from_iterable([
                message.attachments
                async for message in channel.history(limit=None)
            ]))
        for image in image_list:
            # Get the image name
            filename = Path(urlparse(image.url).path).stem
            # Replace underscore with space
            filename = filename.replace("_", " ")

            if filename.startswith("Alice Briarwood"):
                ctx.game.alice = int(filename.split()[-1])
                break

        # Clues
        for name in gamedata.CHARACTERS:
            # Create blank values to fill out
            ctx.game.clue_assignments[name] = []

            channel = ctx.text_channels[f"{name}-clues"]
            current_clue = 90
            image_list = list(itertools.chain.from_iterable([
                message.attachments
                async for message in channel.history(limit=None, oldest_first=True)
            ]))
            for image in image_list:
                # Get the image name
                filename = Path(urlparse(image.url).path).stem

                # Replace underscore with space
                filename = filename.replace("_", " ")

                # Ignore character cards
                if filename in gamedata.CHARACTERS.values():
                    continue

                # Motives
                elif filename.split()[0] == "Motive":
                    ctx.game.motives[name] = filename.split()[1]

                # Suspects
                elif filename in gamedata.SUSPECTS.values():
                    for suspect in gamedata.SUSPECTS:
                        if filename == gamedata.SUSPECTS[suspect]:
                            ctx.game.suspects_drawn[current_clue] = suspect
                            break

                # Locations
                elif filename in gamedata.LOCATIONS.values():
                    for location in gamedata.LOCATIONS:
                        if filename == gamedata.LOCATIONS[location]:
                            ctx.game.locations_drawn[current_clue] = location
                            break

                # Searching cards
                elif filename in gamedata.SEARCHING.values():
                    for item in gamedata.SEARCHING:
                        if filename == gamedata.SEARCHING[item]:
                            ctx.game.searching[name].append(item)
                            break

                # Clue cards
                else:
                    try:
                        time, choice = [int(num) for num in filename.split("-", maxsplit=2)]
                        current_clue = time
                        ctx.game.clue_assignments[name].append(time)
                        ctx.game.picked_clues[time] = choice
                    except TypeError:
                        print(filename)

    @commands.command(aliases=["PDF"])
    async def pdf(self, ctx, file_name=""):
        """Exports the game to a PDF"""

        # If the bot does not have game data loaded, attempt to import
        if not ctx.game.start_time:
            await ctx.send("Gathering game data...")
            await self.import_data(ctx)
        # If import failed, display error message and quit
        if not ctx.game.motives:
            asyncio.create_task(ctx.send("Couldn't find game data to export!"))
            return
            
        # Create pdf object
        pdf = PDF(format="letter", unit="in")
        pdf.set_auto_page_break(True, margin=1)

        # Add fonts
        pdf.add_font("Baloo", "", str(BALOO_REGULAR), True)

        pdf.add_font("Built", "sb", str(BUILT_TITLING_SB), True)
        pdf.add_font("Built", "bd", str(BUILT_TITLING_BD), True)

        # Cover page
        pdf.add_page()
        # Heading
        self.heading(ctx, pdf, "Alice is Missing", COVER_TITLE_FONT, align="C", y=COVER_TITLE_Y)
        # Poster
        poster = utils.POSTER_DIR / ("Alice Briarwood " + str(ctx.game.alice) + utils.IMAGE_EXT)
        pdf.image(str(poster), COVER_POSTER_X, COVER_POSTER_Y, COVER_POSTER_WIDTH)

        # Create list of player characters
        characters = [character for character in gamedata.CHARACTERS if (character.title() in ctx.game.char_roles())]

        await ctx.send("Building character pages...")

        pm_channels = []
        for i in range(len(characters)):
            # Create pages for each character
            self.generate_char_page(ctx, pdf, characters[i].lower())
            
            # Create list of character pairs
            for j in range(i+1, len(characters)):
                pm_channels.append((characters[i], characters[j]))

        await ctx.send("Collecting messages...")

        # Group chat export
        pdf.add_page()
        self.heading(ctx, pdf, "Group Chat", PM_TITLE_FONT, gap=MESSAGES_TITLE_TEXT_GAP, y=MESSAGES_TITLE_Y)
        channel = "group-chat"
        await self.channel_export(ctx, pdf, channel)

        # Chat message exports
        for a, b in pm_channels:
            channel = a + "-" + b + "-pm"
            # Make sure channel has messages
            last_message = await ctx.text_channels[channel].history(limit=1).flatten()
            if last_message:
                title = a.title() + "/" + b.title()
                pdf.add_page()
                self.heading(ctx, pdf, title, PM_TITLE_FONT, gap=MESSAGES_TITLE_TEXT_GAP, y=MESSAGES_TITLE_Y)

                await self.channel_export(ctx, pdf, channel)

        # Output the file
        if not file_name:
            file_name = ctx.guild.name
        
        out = str(utils.PDF_EXPORT_DIR / (file_name + ".pdf"))
        pdf.output(out)
        await ctx.send("PDF created!")

    def heading(self, ctx, pdf, title: str, font, align='', y=None, gap:float=0):
        """Add a heading to the current page"""

        pdf.set_font(*font)
        if y != None:
            pdf.set_y(y)
        pdf.cell(0, 0, title, align=align)
        pdf.ln(gap)

    def generate_char_page(self, ctx, pdf, character):
        """Creates a character page"""

        pdf.add_page()

        # Name at top left
        pdf.set_xy(CHAR_TITLE_X, CHAR_TITLE_Y)
        pdf.set_font(*CHAR_TITLE_FONT)
        title = "\n".join(gamedata.CHARACTERS[character].split())
        pdf.multi_cell(0, CHAR_TITLE_HEIGHT, title)

        # Character and motive cards
        name = gamedata.CHARACTERS[character]
        card = utils.CHARACTER_IMAGE_DIR / (name + utils.IMAGE_EXT)
        pdf.image(str(card), CHAR_CARD_LEFT, CHAR_CARD_TOP, CHAR_CARD_WIDTH)

        motive = ctx.game.motives[character]
        card = utils.MOTIVE_DIR / (f"Motive {motive}{utils.IMAGE_EXT}")
        pdf.image(str(card), CHAR_CARD_LEFT, MOTIVE_CARD_TOP, CHAR_CARD_WIDTH)

        # Clues
        current_y = CLUE_CARDS_TOP
        for clue in ctx.game.clue_assignments[character]:
            # Skip 90 and 10 clues
            if clue == 90 or clue == 10:
                continue

            # Clue label
            label = str(clue)
            label_width = pdf.get_string_width(label)
            label_x = CLUE_LABEL_X
            label_y = current_y + CLUE_LABEL_Y_OFFSET
            pdf.set_xy(label_x, label_y)
            pdf.set_font(*CLUE_LABEL_FONT)
            pdf.cell(label_width, 0, label)

            # Clue card
            choice = ctx.game.picked_clues[clue]
            card = utils.CLUE_DIR / str(clue) / f"{clue}-{choice}{utils.IMAGE_EXT}"
            pdf.image(str(card), CLUE_CARD_LEFT, current_y, CLUE_CARD_WIDTH)


            # Suspect card
            if clue in ctx.game.suspects_drawn:
                suspect = gamedata.SUSPECTS[ctx.game.suspects_drawn[clue]]
                card = utils.SUSPECT_IMAGE_DIR / f"{suspect}{utils.IMAGE_EXT}"
            elif clue in ctx.game.locations_drawn:
                location = gamedata.LOCATIONS[ctx.game.locations_drawn[clue]]
                card = utils.LOCATION_IMAGE_DIR / f"{location}{utils.IMAGE_EXT}"
            
            pdf.image(str(card), SUSPECT_CARD_LEFT, current_y, CLUE_CARD_WIDTH)

            current_y += CLUE_CARD_HEIGHT + CLUE_CLUE_GAP

    async def channel_export(self, ctx, pdf, channel):
        """
        Takes all messages from a text channel and adds them 
        to the current page
        """

        pdf.set_font(*PM_FONT)
        channel = ctx.text_channels[channel]
        async for message in channel.history(limit=None, oldest_first=True):
            # Time remaining
            delta = message.created_at - ctx.game.start_time
            dseconds = delta.seconds
            time = gamedata.GAME_LENGTH - dseconds
            stamp = f"({utils.time_string(time)})"

            # Name
            author = message.author.display_name.split()[0]

            line = utils.remove_emojis(message.clean_content)
            line = f"{author}: {line} {stamp}"

            pdf.multi_cell(0, MESSAGES_LINE_HEIGHT, line)

    @commands.command()
    async def txt(self, ctx):
        """Gets all messages from a guild and writes to a .txt file"""

        await ctx.send("Downloading...")
        # make folder for messages
        message_dir = utils.WHITE_RABBIT_DIR / ctx.guild.name
        message_dir.mkdir(parents=True, exist_ok=True)

        # Download messages
        for channel in ctx.guild.text_channels:
            messages = [
                " ".join((
                    message.created_at.strftime('%Y-%m-%d %H:%M'),
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
    bot.add_cog(Export(bot))
