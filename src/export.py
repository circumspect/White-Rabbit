# 3rd-party
import discord
from discord.ext import commands
from fpdf import FPDF
# Local
import gamedata
import utils

# PDF export constants
# Dimensions
TITLE_CELL_HEIGHT = 0.8
TITLE_CARD_WIDTH = 2

# Positions
CHAR_IMAGE_X = 3.5
CHAR_IMAGE_Y = 0.4
CHAR_MOTIVE_GAP = 0.5
MOTIVE_IMAGE_X = CHAR_IMAGE_X + TITLE_CARD_WIDTH + CHAR_MOTIVE_GAP

# Fonts
COVER_TITLE_FONT = "Essays1743"
CHAR_TITLE_FONT = "Bebas"

# Font paths
FONT_DIR = utils.WHITE_RABBIT_DIR / "Fonts"

BEBAS_DIR = FONT_DIR / "bebas_neue"
BEBAS_NEUE = BEBAS_DIR / "BebasNeue-Regular.ttf"

ESSAYS_DIR = FONT_DIR / "Essays1743"
ESSAYS_1743 = ESSAYS_DIR / "Essays1743.ttf"
ESSAYS_1743_B = ESSAYS_DIR / "Essays1743-Bold.ttf"



class PDF(FPDF):
    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
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

        # Create pdf object
        pdf = PDF(format='letter', unit='in')
        pdf.alias_nb_pages()

        # Add fonts
        pdf.add_font('Bebas', '', str(BEBAS_NEUE), True)

        pdf.add_font('Essays1743', '', str(ESSAYS_1743), True)
        pdf.add_font('Essays1743', 'B', str(ESSAYS_1743), True)

        # Cover page
        pdf.add_page()
        pdf.set_font(COVER_TITLE_FONT, 'B', 60)
        pdf.cell(0, TITLE_CELL_HEIGHT, "Alice is Missing", align='C')

        # Create pages for each character
        for character in ctx.game.char_roles():
            self.generate_char_page(ctx, pdf, character.lower())

        # Output the file
        pdf.output('alice.pdf', 'F')

    def generate_char_page(self, ctx, pdf, character):
        pdf.add_page()

        # Name at top left
        pdf.set_font(CHAR_TITLE_FONT, '', 60)
        title = "\n".join(gamedata.CHARACTERS[character].split())
        pdf.multi_cell(0, TITLE_CELL_HEIGHT, title)

        # Character and motive cards top right
        char_image = str(utils.MASTER_PATHS[character])
        pdf.image(char_image, CHAR_IMAGE_X, CHAR_IMAGE_Y, TITLE_CARD_WIDTH)

        motive_image = str(utils.MOTIVE_DIR / ("Motive " + str(ctx.game.motives[character]) + ".png"))
        pdf.image(motive_image, MOTIVE_IMAGE_X, CHAR_IMAGE_Y, TITLE_CARD_WIDTH)

def setup(bot):
    bot.add_cog(Export(bot))
