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
CHAR_TITLE_CARD_GAP = 0.2
CHAR_CARD_TOP = CHAR_TITLE_Y + CHAR_TITLE_HEIGHT * 2 + CHAR_TITLE_CARD_GAP
# Motive card location
CHAR_CARD_MOTIVE_GAP = 0.2
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

# Voicemails
VOICEMAIL_TITLE_Y = 8.5
VOICEMAIL_TITLE = "Voicemail"
VOICEMAIL_TEXT_OFFSET = 0
VOICEMAIL_TITLE_TEXT_GAP = 0.2
VOICEMAIL_TEXT_LINE_HEIGHT = 0.2
VOICEMAIL_Y = VOICEMAIL_TITLE_Y + VOICEMAIL_TITLE_TEXT_GAP


# Conclusions page
# Title
CONCLUSION_TITLE = "Conclusions"
CONCLUSION_TITLE_Y = 0.8

# Row 1
CONCLUSION_TITLE_ROW1_LABEL_GAP = 0.8
CONCLUSION_ROW1_LABEL_Y = CONCLUSION_TITLE_Y + CONCLUSION_TITLE_ROW1_LABEL_GAP
# Character card
CONCLUSION_LABEL_IMAGE_GAP = 0.8
CONCLUSION_CHAR_CARD_X = 0.5
CONCLUSION_ROW1_IMAGE_Y = CONCLUSION_TITLE_Y + CONCLUSION_LABEL_IMAGE_GAP
CONCLUSION_CARD_WIDTH = 2
CONCLUSION_CARD_HEIGHT = CONCLUSION_CARD_WIDTH * CARD_RATIO
# 10 minute clue card
CONCLUSION_CLUE_CARD_X = PAGE_WIDTH/2 - CONCLUSION_CARD_WIDTH/2
# Location card
CONCLUSION_LOCATION_CARD_X = 8.5 - CONCLUSION_CHAR_CARD_X - CONCLUSION_CARD_WIDTH

# Row 2
CONCLUSION_ROW1_ROW2_GAP = 0.2
CONCLUSION_ROW2_LABEL_Y = CONCLUSION_ROW1_IMAGE_Y + CONCLUSION_CARD_HEIGHT + CONCLUSION_ROW1_ROW2_GAP
# Suspect cards
CONCLUSION_CHAR_SUSPECT_GAP = 0.3
CONCLUSION_SUSPECT_CARD_X = CONCLUSION_CHAR_CARD_X
CONCLUSION_ROW2_IMAGE_Y = CONCLUSION_ROW2_LABEL_Y + CONCLUSION_LABEL_IMAGE_GAP

# Body text
CONCLUSION_BODY_X = 3.3
CONCLUSION_BODY_Y = 7
CONCLUSION_BODY_RIGHT = 7.8
CONCLUSION_BODY_WIDTH = CONCLUSION_BODY_RIGHT - CONCLUSION_BODY_X
CONCLUSION_BODY_LINE_HEIGHT = 0.3

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
VOICEMAIL_TITLE_FONT = ("Built", '', 20)
VOICEMAIL_FONT = ("Abel", '', 12)

# Conclusions page
CONCLUSION_TITLE_FONT = ("Built", 'sb', 72)
CONCLUSION_BODY_FONT = ("Abel", '', 18)

# Message pages
PM_TITLE_FONT = ("Built", 'sb', 24)
PM_FONT = ("Abel", '', 12)

# Footer
WATERMARK_FONTS = (("Abel", '', 12), ("Abel", '', 16))
PAGE_NUMBER_FONT = WATERMARK_FONTS[1]


# Font paths
FONT_DIR = utils.RESOURCE_DIR / "Fonts"

BUILT_DIR = FONT_DIR / "built_titling"
BUILT_TITLING_RG = BUILT_DIR / "built titling rg.ttf"
BUILT_TITLING_SB = BUILT_DIR / "built titling sb.ttf"
BUILT_TITLING_BD = BUILT_DIR / "built titling bd.ttf"

ABEL_DIR = FONT_DIR / "Abel"
ABEL_REGULAR = ABEL_DIR / "Abel-Regular.ttf"


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
        channel = ctx.text_channels["group-chat"]
        async for message in channel.history(limit=None, oldest_first=True):
            if "Hey! Sorry for the big group text" in message.clean_content:
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
            # Replace Discord's automatically added underscores with spaces
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
                        time, choice = [num for num in filename.split("-", maxsplit=2)]

                        # Split in case of old filenames
                        choice = choice.split()[0]
                        
                        time = int(time)
                        choice = int(choice)

                        current_clue = time
                        # If 10 minute clue card, mark ten_char
                        if time == 10:
                            ctx.game.ten_char = name

                        ctx.game.clue_assignments[name].append(time)
                        ctx.game.picked_clues[time] = choice
                    except:
                        # If still can't determine image type, log to console
                        # and ignore
                        print(filename)
        
        # Look for coin flip
        channel = ctx.text_channels[f"{ctx.game.ten_char}-clues"]
        async for message in channel.history(limit=5):
            text = message.clean_content.strip().title()
            if text in ("Heads", "Tails"):
                ctx.game.ending_flip = text
                break

        # Voicemails
        channel = ctx.text_channels["voicemails"]
        async for message in channel.history(limit=None, oldest_first=True):
            # Name
            character = message.author.display_name.lower().split()[0]
            voicemail = utils.remove_emojis(message.clean_content)
            ctx.game.voicemails[character] = voicemail.strip("|")

    @commands.command(aliases=["PDF"])
    async def pdf(self, ctx, file_name=""):
        """Exports the game to a PDF"""

        # Import game data
        await ctx.send("Gathering game data...")
        await self.import_data(ctx)

        if not ctx.game.motives:
            asyncio.create_task(ctx.send("Couldn't find game data to export!"))
            return
            
        # Create pdf object
        pdf = PDF(format="letter", unit="in")
        pdf.set_auto_page_break(True, margin=1)

        # Add fonts
        pdf.add_font("Built", "", str(BUILT_TITLING_RG), True)
        pdf.add_font("Built", "sb", str(BUILT_TITLING_SB), True)
        pdf.add_font("Built", "bd", str(BUILT_TITLING_BD), True)

        pdf.add_font("Abel", "", str(ABEL_REGULAR), True)


        # Cover page
        pdf.add_page()
        # Heading
        self.heading(ctx, pdf, "Alice is Missing", COVER_TITLE_FONT, align="C", y=COVER_TITLE_Y)
        # Poster
        poster = utils.POSTER_DIR / f"Alice Briarwood {ctx.game.alice}{utils.IMAGE_EXT}"
        pdf.image(str(poster), COVER_POSTER_X, COVER_POSTER_Y, COVER_POSTER_WIDTH)

        # Create list of player characters
        characters = [character.lower() for character in ctx.game.char_roles()]

        await ctx.send("Building character pages...")

        pm_channels = []
        for i, character in enumerate(characters):
            # Create pages for each character
            self.generate_char_page(ctx, pdf, character)
            
            # Create list of character pairs
            for j in range(i+1, len(characters)):
                pm_channels.append((character, characters[j]))

        # Conclusion/ending page
        self.conclusion_page(ctx, pdf)

        await ctx.send("Collecting messages...")

        # Group chat export
        pdf.add_page()
        self.heading(ctx, pdf, "Group Chat", PM_TITLE_FONT, gap=MESSAGES_TITLE_TEXT_GAP, y=MESSAGES_TITLE_Y)
        await self.channel_export(ctx, pdf, "group-chat")

        # Chat message exports
        for a, b in pm_channels:
            channel = f"{a}-{b}-pm"
            # Make sure channel has messages
            last_message = await ctx.text_channels[channel].history(limit=1).flatten()
            if last_message:
                title = f"{a.title()}/{b.title()}"
                pdf.add_page()
                self.heading(ctx, pdf, title, PM_TITLE_FONT, gap=MESSAGES_TITLE_TEXT_GAP, y=MESSAGES_TITLE_Y)

                await self.channel_export(ctx, pdf, channel)

        # Output the file
        if not file_name:
            file_name = ctx.guild.name
        
        out = (utils.PDF_EXPORT_DIR / file_name).with_suffix(".pdf")
        pdf.output(str(out))
        await ctx.send("PDF created!")

    def heading(self, ctx, pdf, title: str, font, align='', y=None, gap:float=0):
        """Add a heading to the current page"""

        pdf.set_font(*font)
        if y is not None:
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
        card = (utils.CHARACTER_IMAGE_DIR / name).with_suffix(utils.IMAGE_EXT)
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
        
        # Voicemail
        pdf.set_font(*VOICEMAIL_TITLE_FONT)
        pdf.set_y(VOICEMAIL_TITLE_Y)
        pdf.cell(0, 0, VOICEMAIL_TITLE)
        pdf.set_font(*VOICEMAIL_FONT)
        pdf.set_y(VOICEMAIL_Y)
        pdf.multi_cell(0, VOICEMAIL_TEXT_LINE_HEIGHT, ctx.game.voicemails[character])

    def conclusion_page(self, ctx, pdf):
        """Create conclusions page based on 10 minute clue"""
        
        # Add title
        pdf.add_page()
        pdf.set_y(CONCLUSION_TITLE_Y)
        pdf.set_font(*CONCLUSION_TITLE_FONT)
        pdf.cell(0, 0, CONCLUSION_TITLE)

        # Add character card
        card = utils.MASTER_PATHS[ctx.game.ten_char]
        pdf.image(str(card), CONCLUSION_CHAR_CARD_X, CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add clue card
        card = utils.CLUE_DIR / "10" / f"10-{ctx.game.picked_clues[10]}{utils.IMAGE_EXT}"
        pdf.image(str(card), CONCLUSION_CLUE_CARD_X, CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add location card
        card = utils.MASTER_PATHS[ctx.game.locations_drawn[20]]
        pdf.image(str(card), CONCLUSION_LOCATION_CARD_X, CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add first suspect card
        card = utils.MASTER_PATHS[ctx.game.suspects_drawn[30]]
        pdf.image(str(card), CONCLUSION_SUSPECT_CARD_X, CONCLUSION_ROW2_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Find involved parties
        investigator = gamedata.CHARACTERS[ctx.game.ten_char]
        location = gamedata.LOCATIONS[ctx.game.locations_drawn[20]]
        culprit = gamedata.SUSPECTS[ctx.game.suspects_drawn[30]]
        if culprit == "Mr Halvert":
            culprit = "Mr. Halvert"
        # Check for second culprit
        try:
            second_culprit = ctx.game.suspects_drawn[10]
            if second_culprit == "Mr Halvert":
                second_culprit = "Mr. Halvert"
        except KeyError:
            pass
        
        # Add conclusion body text
        text = f"{investigator} went to the {location} searching for Alice, where {gamedata.PRONOUNS[ctx.game.ten_char][0]} found "
        ending = ctx.game.picked_clues[10]
        if ending == 1:
            text += f""
        elif ending == 2:
            text += f"Alice's body, left there by {culprit}, who then returned and saw {investigator.split()[0]}. {culprit} then chased after {ctx.game.ten_char.title()}"
            
            if ctx.game.ending_flip == "Heads":
                text += f", who barely managed to escape."
            elif ctx.game.ending_flip == "Tails":
                text += f" and caught {gamedata.PRONOUNS[ctx.game.ten_char][1]}."

        elif ending == 3:
            text += f""

        pdf.set_font(*CONCLUSION_BODY_FONT)
        pdf.set_xy(CONCLUSION_BODY_X, CONCLUSION_BODY_Y)
        pdf.multi_cell(CONCLUSION_BODY_WIDTH, CONCLUSION_BODY_LINE_HEIGHT, text)

    async def channel_export(self, ctx, pdf, channel):
        """
        Takes all messages from a text channel and adds them 
        to the current page
        """

        pdf.set_font(*PM_FONT)
        channel = ctx.text_channels[channel]
        async for message in channel.history(limit=None, oldest_first=True):
            # Name
            author = message.author.display_name.split()[0]

            # Remove emojis then strip whitespace at start/end
            line = utils.remove_emojis(message.clean_content).strip()
            
            # If message looks like a command attempt, ignore it
            if utils.is_command(line):
                continue

            # If message is out of character, ignore
            if ctx.game.ooc_strip:
                if line.startswith("(") and line.endswith(")"):
                    continue

            # If string is now empty, move to next message
            if line == "":
                continue

            line = f"{author}: {line}"

            # Time remaining
            delta = message.created_at - ctx.game.start_time
            dseconds = delta.seconds
            time = gamedata.GAME_LENGTH - dseconds
            if time >= 0:
                # Don't display timestamp if after game has ended
                stamp = f"({utils.time_string(time)})"
                line += f" {stamp}"

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
