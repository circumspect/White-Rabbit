import itertools
from urllib.parse import urlparse
from pathlib import Path
import shutil


import asyncio
import discord
from discord.ext import commands
from fpdf import FPDF

import gamedata
import utils

# PDF export constants - all measurements are in inches
PAGE_WIDTH = 8.5  # Letter size paper inch width
CARD_RATIO = 1057 / 757  # Card height to width ratio
PAGE_NUMBER_Y = -0.8  # Vertical position of page number

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
CHAR_IMAGE_X = 3.5
# Top edge of character/motive cards to top edge of page
CHAR_IMAGE_Y = 0.4
# Gap between character card and motive card
CHAR_MOTIVE_GAP = 0.5
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


# PM Pages
PM_TITLE_HEIGHT = 1
PM_LINE_HEIGHT = 0.3


# Fonts
COVER_TITLE_FONT = ("Built", 'bd', 80)
CHAR_TITLE_FONT = ("Built", 'sb', 60)
PAGE_NUMBER_FONT = ("Essays", '', 16)
PM_TITLE_FONT = ("Essays", '', 24)
PM_FONT = ("Essays", '', 12)

# Font paths
FONT_DIR = utils.WHITE_RABBIT_DIR / "Fonts"

BEBAS_DIR = FONT_DIR / "bebas_neue"
BEBAS_NEUE = BEBAS_DIR / "BebasNeue-Regular.ttf"

BUILT_DIR = FONT_DIR / "built_titling"
BUILT_TITLING_SB = BUILT_DIR / "built titling sb.ttf"
BUILT_TITLING_BD = BUILT_DIR / "built titling bd.ttf"

ESSAYS_DIR = FONT_DIR / "Essays1743"
ESSAYS_1743 = ESSAYS_DIR / "Essays1743.ttf"
ESSAYS_1743_B = ESSAYS_DIR / "Essays1743-Bold.ttf"


class PDF(FPDF):
    # Page footer
    def footer(self):
        # Page number
        self.set_y(PAGE_NUMBER_Y)
        self.set_font(*PAGE_NUMBER_FONT)

        page_number_text = str(self.page_no() - 1)
        if page_number_text != "0":
            self.cell(0, 1, page_number_text, 0, 0, 'R')


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def import_data(self, ctx):
        """imports data from message history"""
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
                # get the image name
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
        if not ctx.game.started:
            await self.import_data(ctx)
        # If import failed, display error message and quit
        if not ctx.game.motives:
            asyncio.create_task(ctx.send("Couldn't find game data to export!"))
            return

        # Create pdf object
        pdf = PDF(format="letter", unit="in")
        pdf.alias_nb_pages()

        # Add fonts
        pdf.add_font("Built", "sb", str(BUILT_TITLING_SB), True)
        pdf.add_font("Built", "bd", str(BUILT_TITLING_BD), True)

        pdf.add_font("Essays", "", str(ESSAYS_1743), True)
        pdf.add_font("Essays", "B", str(ESSAYS_1743_B), True)

        # Cover page
        pdf.add_page()
        pdf.set_font(*COVER_TITLE_FONT)
        pdf.cell(0, CHAR_TITLE_HEIGHT, "Alice is Missing", align="C")

        # Create list of player characters
        characters = [character for character in gamedata.CHARACTERS if (character.title() in ctx.game.char_roles())]

        pm_channels = []
        for i in range(len(characters)):
            # Create pages for each character
            self.generate_char_page(ctx, pdf, characters[i].lower())
            
            # Create list of character pairs
            for j in range(i+1, len(characters)):
                pm_channels.append((characters[i], characters[j]))

        # Chat message exports
        for a, b in pm_channels:
            pdf.add_page()
            pdf.set_font(*PM_TITLE_FONT)
            pdf.cell(0, PM_TITLE_HEIGHT, a.title() + "/" + b.title())
            pdf.ln()

            channel = a + "-" + b + "-pm"
            await self.channel_export(ctx, pdf, channel)

        # Output the file
        pdf.output("alice.pdf")

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
        pdf.set_font(*PM_FONT)
        channel = ctx.text_channels[channel]
        async for message in channel.history(limit=None, oldest_first=True):
            line = message.content
            pdf.multi_cell(0, PM_LINE_HEIGHT, line)

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
