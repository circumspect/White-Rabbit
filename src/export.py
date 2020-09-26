# Built-in
import datetime
import itertools
import math
from pathlib import Path
import shutil
from urllib.parse import urlparse
# 3rd-party
import asyncio
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
CHAR_TITLE_HEIGHT = 0.8
# Character/motive cards
# Dimensions of character/motive card images
CHAR_IMAGE_WIDTH = 2
CHAR_IMAGE_HEIGHT = CHAR_IMAGE_WIDTH * CARD_RATIO
CHAR_TITLE_X = 0.5
CHAR_TITLE_Y = 1

# Positions
# Left edge of character card to left edge of page
CHAR_IMAGE_X = 3.8
# Top edge of character/motive cards to top edge of page
CHAR_IMAGE_Y = 0.4
# Gap between character card and motive card
CHAR_MOTIVE_GAP = 0.3
# Calculate left edge of motive card - DO NOT TOUCH
MOTIVE_IMAGE_X = CHAR_IMAGE_X + CHAR_IMAGE_WIDTH + CHAR_MOTIVE_GAP


# Clue cards
# Dimensions of character/motive card images
CLUE_IMAGE_WIDTH = 1.75
CLUE_IMAGE_HEIGHT = CLUE_IMAGE_WIDTH * CARD_RATIO

# Gap between clue card images
CLUE_IMAGE_GAP = 0.25
# Vertical gap between character/motive cards and clue cards
CHAR_CLUE_GAP = 0.5
# Vertical gap between clue cards and corresponding suspect cards
CLUE_SUSPECT_GAP = 0.25
# Calculations - DO NOT TOUCH
CLUE_IMAGE_LEFT = PAGE_WIDTH/2 - 1.5*CLUE_IMAGE_GAP - 2*CLUE_IMAGE_WIDTH
CLUE_IMAGE_Y = CHAR_IMAGE_Y + CHAR_IMAGE_HEIGHT + CHAR_CLUE_GAP
SUSPECT_IMAGE_Y = CLUE_IMAGE_Y + CLUE_IMAGE_HEIGHT + CLUE_SUSPECT_GAP


# Group chat/PM pages
MESSAGES_TITLE_Y = 0.5
MESSAGES_TITLE_TEXT_GAP = 0.3
MESSAGES_LINE_HEIGHT = 0.25


# Fonts
COVER_TITLE_FONT = ("Built", 'bd', 80)
CHAR_TITLE_FONT = ("Built", 'sb', 60)

PM_TITLE_FONT = ("Built", 'sb', 24)
PM_FONT = ("Baloo", '', 12)

WATERMARK_FONTS = (("Baloo", '', 12), ("Baloo", '', 16))
PAGE_NUMBER_FONT = WATERMARK_FONTS[1]


# Font paths
FONT_DIR = utils.WHITE_RABBIT_DIR / "Fonts"

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

    @commands.command()
    async def pdf(self, ctx):
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
        out = str(utils.PDF_EXPORT_DIR / (ctx.guild.name + ".pdf"))
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

        # Character and motive cards top right
        char_image = utils.MASTER_PATHS[character]
        pdf.image(str(char_image), CHAR_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        motive_image = utils.MOTIVE_DIR / f"Motive {ctx.game.motives[character]}.png"
        pdf.image(str(motive_image), MOTIVE_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        # Clue and corresponding suspect cards in two rows
        image_x = CLUE_IMAGE_LEFT

        for clue in ctx.game.clue_assignments[character]:
            # Don't print 10 minute image
            if clue == 10:
                continue

            # Add clue card to page
            clue_image = utils.CLUE_DIR / str(clue) / f"{clue}-{ctx.game.picked_clues[clue]}.png"
            image_y = CLUE_IMAGE_Y
            if clue == 90:
                image_y += (CLUE_IMAGE_HEIGHT + CLUE_SUSPECT_GAP) / 2

            pdf.image(str(clue_image), image_x, image_y, CLUE_IMAGE_WIDTH)

            if clue != 90:
                # Add suspect card to page
                for time in ctx.game.suspects_drawn:
                    if time == clue:
                        suspect = ctx.game.suspects_drawn[time]
                        break
                else:
                    for time in ctx.game.locations_drawn:
                        if time == clue:
                            suspect = ctx.game.locations_drawn[time]
                            break

                suspect_image = utils.MASTER_PATHS[suspect]
                pdf.image(str(suspect_image), image_x, SUSPECT_IMAGE_Y, CLUE_IMAGE_WIDTH)

            # Adjust for next column
            image_x += CLUE_IMAGE_WIDTH + CLUE_IMAGE_GAP

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
            stamp = utils.time_string(time)

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
