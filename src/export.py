# 3rd-party
import discord
from discord.ext import commands
from fpdf import FPDF
# Local
import gamedata
import utils

# PDF export constants - all measurements are in inches
PAGE_WIDTH = 8.5 # Letter size paper inch width
CARD_RATIO = 1057 / 757 # Card height to width ratio

# Character Pages
TITLE_CELL_HEIGHT = 0.8
# Character/motive cards
# Dimensions of character/motive card images
CHAR_IMAGE_WIDTH = 2
CHAR_IMAGE_HEIGHT = CHAR_IMAGE_WIDTH * CARD_RATIO

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
COVER_TITLE_FONT = ("Built", 'bd', 96)
CHAR_TITLE_FONT = ("Built", 'sb', 60)

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
        # Position 3/4 inch from bottom
        self.set_y(-0.75)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def pdf(self, ctx):
        """Exports the game to a PDF"""

        # Check if game was run and if so use dicts created during play
        fresh = ctx.game.started

        # Create pdf object
        pdf = PDF(format='letter', unit='in')
        pdf.alias_nb_pages()

        # Add fonts
        pdf.add_font('Built', 'sb', str(BUILT_TITLING_SB), True)
        pdf.add_font('Built', 'bd', str(BUILT_TITLING_BD), True)

        pdf.add_font('Essays1743', '', str(ESSAYS_1743), True)
        pdf.add_font('Essays1743', 'B', str(ESSAYS_1743), True)

        # Cover page
        pdf.add_page()
        family, font, size = COVER_TITLE_FONT
        pdf.set_font(family, font, size)
        pdf.cell(0, TITLE_CELL_HEIGHT, "Alice is Missing", align='C')

        # Create pages for each character
        for character in ctx.game.char_roles():
            self.generate_char_page(ctx, pdf, character.lower(), fresh)

        # Output the file
        pdf.output('alice.pdf', 'F')

    def generate_char_page(self, ctx, pdf, character, fresh: bool):
        pdf.add_page()

        # Name at top left
        family, font, size = CHAR_TITLE_FONT
        pdf.set_font(family, font, size)
        title = "\n".join(gamedata.CHARACTERS[character].split())
        pdf.multi_cell(0, TITLE_CELL_HEIGHT, title)

        # Character and motive cards top right
        char_image = str(utils.MASTER_PATHS[character])
        pdf.image(char_image, CHAR_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        motive_image = str(utils.MOTIVE_DIR / ("Motive " + str(ctx.game.motives[character]) + utils.IMAGE_EXT))
        pdf.image(motive_image, MOTIVE_IMAGE_X, CHAR_IMAGE_Y, CHAR_IMAGE_WIDTH)

        # Clue and corresponding suspect cards in two rows
        image_x = CLUE_IMAGE_LEFT

        for clue in ctx.game.clue_assignments[character]:
            # Add clue card to page
            clue_image = str(utils.CLUE_DIR / str(clue) / (str(clue) + "-" + str(ctx.game.picked_clues[clue]) + utils.IMAGE_EXT))
            image_y = CLUE_IMAGE_Y
            if clue == 90:
                image_y += (CLUE_IMAGE_HEIGHT + CLUE_SUSPECT_GAP)/2

            pdf.image(clue_image, image_x, image_y, CLUE_IMAGE_WIDTH)

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

def setup(bot):
    bot.add_cog(Export(bot))
