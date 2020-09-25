# 3rd-party
import asyncio
import discord
from discord.ext import commands
from fpdf import FPDF
# Local
import gamedata
import shutil
import utils

# PDF export constants - all measurements are in inches
PAGE_WIDTH = 8.5  # Letter size paper inch width
CARD_RATIO = 1057 / 757  # Card height to width ratio
PAGE_NUMBER_Y = -0.8  # Vertical position of page number

# Character Pages
TITLE_CELL_HEIGHT = 0.8
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


# Fonts
COVER_TITLE_FONT = ("Built", 'bd', 80)
CHAR_TITLE_FONT = ("Built", 'sb', 60)
PAGE_NUMBER_FONT = ("Essays", '', 16)

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
        family, font, size = PAGE_NUMBER_FONT
        self.set_font(family, font, size)
        
        page_number_text = str(self.page_no() - 1)
        if page_number_text != "0":
            self.cell(0, 1, page_number_text, 0, 0, 'R')


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def import_data(self, ctx):
        names = list(gamedata.CHARACTERS)

        for name in names:
            # Create blank values to fill out
            ctx.game.clue_assignments[name] = []

            channel = ctx.text_channels[name + "-clues"]
            current_clue = 90
            image_list = [message.attachments async for message in channel.history(limit=None, oldest_first=True)]
            for image in image_list:
                if not image:
                    continue

                url = image[0].url
                filename = url.split("/")[-1]

                # Strip extension
                filename = filename.split(".")[0]

                # Replace underscore with space
                filename = filename.replace("_", " ")

                if filename in gamedata.CHARACTERS.values():
                    # Ignore character cards
                    continue
                elif filename.split()[0] == "Motive":
                    # Motives
                    ctx.game.motives[name] = filename.split()[1]
                elif filename in gamedata.SUSPECTS.values():
                    # Suspects
                    for suspect in gamedata.SUSPECTS:
                        if filename == gamedata.SUSPECTS[suspect]:
                            ctx.game.suspects_drawn[current_clue] = suspect
                            break
                elif filename in gamedata.LOCATIONS.values():
                    # Locations
                    for location in gamedata.LOCATIONS:
                        if filename == gamedata.LOCATIONS[location]:
                            ctx.game.locations_drawn[current_clue] = location
                            break
                elif filename in gamedata.SEARCHING.values():
                    # Searching cards
                    for item in gamedata.SEARCHING:
                        if filename == gamedata.SEARCHING[item]:
                            ctx.game.searching[name].append(item)
                            break
                else:
                    # Clue cards
                    try:
                        time = int(filename.split("-")[0])
                        current_clue = time
                        choice = int(filename.split("-")[1])
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
        pdf = PDF(format='letter', unit='in')
        pdf.alias_nb_pages()

        # Add fonts
        pdf.add_font('Built', 'sb', str(BUILT_TITLING_SB), True)
        pdf.add_font('Built', 'bd', str(BUILT_TITLING_BD), True)

        pdf.add_font('Essays', '', str(ESSAYS_1743), True)
        pdf.add_font('Essays', 'B', str(ESSAYS_1743_B), True)

        # Cover page
        pdf.add_page()
        family, font, size = COVER_TITLE_FONT
        pdf.set_font(family, font, size)
        pdf.cell(0, TITLE_CELL_HEIGHT, "Alice is Missing", align='C')

        # Create pages for each character
        for character in ctx.game.char_roles():
            self.generate_char_page(ctx, pdf, character.lower())

        # Chat message exports


        # Output the file
        pdf.output('alice.pdf')

    def generate_char_page(self, ctx, pdf, character):
        pdf.add_page()

        # Name at top left
        pdf.set_xy(CHAR_TITLE_X, CHAR_TITLE_Y)
        family, font, size = CHAR_TITLE_FONT
        pdf.set_font(family, font, size)
        title = "\n".join(gamedata.CHARACTERS[character].split())
        pdf.multi_cell(0, TITLE_CELL_HEIGHT, title)

        # Character and motive cards top right
        char_image = str(utils.MASTER_PATHS[character])
        pdf.image(char_image, CHAR_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        motive_image = str((utils.MOTIVE_DIR / f"Motive {ctx.game.motives[character]}").with_suffix(utils.IMAGE_EXT))
        pdf.image(motive_image, MOTIVE_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        # Clue and corresponding suspect cards in two rows
        image_x = CLUE_IMAGE_LEFT

        for clue in ctx.game.clue_assignments[character]:
            # Don't print 10 minute image
            if clue == 10:
                continue

            # Add clue card to page
            clue_image = (utils.CLUE_DIR / str(clue) / f"{clue}-{ctx.game.picked_clues[clue]}.png")
            image_y = CLUE_IMAGE_Y
            if clue == 90:
                image_y += (CLUE_IMAGE_HEIGHT + CLUE_SUSPECT_GAP)/2

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

                suspect_image = str(utils.MASTER_PATHS[suspect])
                pdf.image(suspect_image, image_x, SUSPECT_IMAGE_Y, CLUE_IMAGE_WIDTH)

            # Adjust for next column
            image_x += (CLUE_IMAGE_WIDTH + CLUE_IMAGE_GAP)

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
