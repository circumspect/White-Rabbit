# Built-in
import asyncio
from pathlib import Path
import shutil
from timeit import default_timer as timer
from urllib.parse import urlparse
# 3rd-party
import discord
from discord.ext import commands
from fpdf import FPDF
# Local
from data import cards, constants, dirs, filepaths, gamedata
from data.dirs import FONT_DIR
from data.wrappers import Bot, Context
from data.localization import LOCALIZATION_DATA
from rabbit import WHITE_RABBIT_DIR
import utils

loc = LOCALIZATION_DATA["commands"]["export"]

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
WATERMARK = (loc["pdf"]["created-by"], LOCALIZATION_DATA["bot-name"])
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
VOICEMAIL_TITLE = loc["pdf"]["voicemail"]
VOICEMAIL_TEXT_OFFSET = 0
VOICEMAIL_TITLE_TEXT_GAP = 0.2
VOICEMAIL_TEXT_LINE_HEIGHT = 0.2
VOICEMAIL_Y = VOICEMAIL_TITLE_Y + VOICEMAIL_TITLE_TEXT_GAP


# Timeline
TIMELINE_TITLE = loc["pdf"]["timeline"]
TIMELINE_TITLE_Y = 0.8

# Conclusions page
CONCLUSION_LABEL_OFFSET = 0.1
CONCLUSION_CARD_WIDTH = 2
CONCLUSION_CARD_HEIGHT = CONCLUSION_CARD_WIDTH * CARD_RATIO

# Title
CONCLUSION_TITLE = loc["pdf"]["conclusion"]
CONCLUSION_TITLE_Y = 0.8

# Row 1
CONCLUSION_TITLE_ROW1_LABEL_GAP = 0.8
CONCLUSION_ROW1_LABEL_Y = CONCLUSION_TITLE_Y + CONCLUSION_TITLE_ROW1_LABEL_GAP
# Character card
CONCLUSION_LABEL_IMAGE_GAP = 0.3
CONCLUSION_CHAR_CARD_X = 0.5
CONCLUSION_ROW1_IMAGE_Y = CONCLUSION_ROW1_LABEL_Y + CONCLUSION_LABEL_IMAGE_GAP
# 10 minute clue card
CONCLUSION_CLUE_CARD_X = PAGE_WIDTH/2 - CONCLUSION_CARD_WIDTH/2
# Location card
CONCLUSION_LOCATION_CARD_X = 8.5 - CONCLUSION_CHAR_CARD_X - CONCLUSION_CARD_WIDTH

# Row 2
CONCLUSION_ROW1_ROW2_GAP = 1
CONCLUSION_ROW2_LABEL_Y = CONCLUSION_ROW1_IMAGE_Y + CONCLUSION_CARD_HEIGHT + CONCLUSION_ROW1_ROW2_GAP
# Suspect cards
CONCLUSION_CHAR_SUSPECT_GAP = 0.3
CONCLUSION_SUSPECT_CARD_GAP = 0.3   # Gap between first and second suspect cards
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

# Timeline
TIMELINE_TITLE_FONT = ("Built", 'sb', 72)

# Conclusions page
CONCLUSION_TITLE_FONT = ("Built", 'sb', 72)
CONCLUSION_LABEL_FONT = ("Built", 'sb', 24)
CONCLUSION_BODY_FONT = ("Abel", '', 18)

# Message pages
PM_TITLE_FONT = ("Built", 'sb', 24)
PM_FONT = ("Abel", '', 12)

# Footer
WATERMARK_FONTS = (("Abel", '', 12), ("Abel", '', 16))
PAGE_NUMBER_FONT = WATERMARK_FONTS[1]


# Font paths
BUILT_DIR = FONT_DIR / "built_titling"
BUILT_TITLING_RG = BUILT_DIR / "built titling rg.ttf"
BUILT_TITLING_SB = BUILT_DIR / "built titling sb.ttf"
BUILT_TITLING_BD = BUILT_DIR / "built titling bd.ttf"

ABEL_DIR = FONT_DIR / "abel"
ABEL_REGULAR = ABEL_DIR / "Abel-Regular.ttf"


class PDF(FPDF):
    # Page footer
    def footer(self):
        # Watermark separator
        self.set_line_width(SEPARATOR_THICKNESS)
        self.line(
            WATERMARK_SEPARATOR_LEFT,
            WATERMARK_SEPARATOR_Y,
            WATERMARK_SEPARATOR_RIGHT,
            WATERMARK_SEPARATOR_Y
        )

        self.set_y(WATERMARK_Y)
        # Watermark
        for i in range(len(WATERMARK)):
            self.set_y(self.get_y() + WATERMARK_GAPS[i])
            self.set_font(*WATERMARK_FONTS[i])
            text = WATERMARK[i]
            width = self.get_string_width(text)
            self.cell(width, 0, text, 0, 0, 'L', link=constants.DOCS_URL)

        # Page number
        self.set_font(*PAGE_NUMBER_FONT)
        page_number_text = str(self.page_no() - 1)

        # Skip cover page
        if page_number_text != "0":
            self.cell(0, 0, page_number_text, 0, 0, 'R')


class Export(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def channel_attachments(self, channel: discord.TextChannel, oldest_first: bool = False):
        url_list = []
        async for message in channel.history(limit=None, oldest_first=oldest_first):
            text = message.clean_content.strip()
            if text.__contains__("raw.githubusercontent.com/"):
                url_list.append(text)

            for attachment in message.attachments:
                url_list.append(attachment.url)

        return url_list

    @staticmethod
    def parse_filename(url: str) -> str:
        filename = Path(urlparse(url).path).stem.replace("_", "-").lower()

        try:
            # Checks for filenames from older versions
            return filepaths.LEGACY_FILENAMES[filename]
        except KeyError:
            tmp = filename.split("-")
            if tmp[0] in cards.SUSPECTS:
                return tmp[0]
            if tmp[0] in cards.CHARACTERS:
                return tmp[0]
            return filename

    async def import_data(self, ctx: Context):
        """imports data from message history"""

        # Find game start
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["texts"]["group-chat"]]
        ctx.game.start_time = None
        async for message in channel.history(limit=None, oldest_first=True):
            # Check if first message matches
            if LOCALIZATION_DATA["stuff-for-charlie"]["first-message"][0:20] in message.clean_content:
                ctx.game.start_time = message.created_at
                break

        # Couldn't find exact match, use first message in channel
        first_message = [message async for message in channel.history(limit=1, oldest_first=True)]

        if not first_message:
            # Channel is empty, so we quit
            return
        else:
            first_message = first_message[0]
            ctx.game.start_time = first_message.created_at

        # Alice
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["resources"]]
        url_list = await self.channel_attachments(channel)

        for url in url_list:
            filename = self.parse_filename(url)

            if filename.startswith("alice-briarwood"):
                ctx.game.alice = int(filename.split("-")[-1])
                break

        # Clues
        for name in cards.CHARACTERS:
            # Create blank values to fill out
            ctx.game.clue_assignments[name] = []

            channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][name]]
            current_clue = 90
            url_list = await self.channel_attachments(channel, True)

            for url in url_list:
                filename = self.parse_filename(url)

                # Ignore character cards
                if filename in cards.CHARACTERS:
                    continue

                # Motives
                elif filename.split("-")[0] == "motive":
                    ctx.game.motives[name] = filename.split("-")[1]

                # Suspects
                elif filename in cards.SUSPECTS:
                    ctx.game.suspects_drawn[current_clue] = filename
                    if current_clue == 10:
                        ctx.game.second_culprit = filename

                # Locations
                elif filename in cards.LOCATIONS:
                    ctx.game.locations_drawn[current_clue] = filename

                # Searching cards
                elif filename in cards.SEARCHING:
                    ctx.game.searching[name].append(filename)

                # Ignore debrief card
                elif filename == "debrief":
                    pass

                # Clue cards
                else:
                    try:
                        # This will raise a ValueError if filename does not
                        # contain "-", so we catch down below
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
                    except ValueError:
                        # If still can't determine image type, log to console
                        # and ignore
                        print(f"{constants.WARNING_PREFIX}Unknown image found in {name.title()}'s clues during export: {filename}")

        # Look for coin flip
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]]
        async for message in channel.history(limit=5):
            text = message.clean_content.strip().title()
            if text in (LOCALIZATION_DATA["flip"]["heads"], LOCALIZATION_DATA["flip"]["tails"]):
                ctx.game.ending_flip = text
                break

        # Voicemails
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["voicemails"]]
        async for message in channel.history(limit=None, oldest_first=True):
            # Name
            character = message.author.display_name.lower().split()[0]

            # Only grab first message from each player
            if not ctx.game.voicemails[character]:
                voicemail = utils.clean_message(ctx, message.clean_content)
                ctx.game.voicemails[character] = voicemail.replace("||", "").replace("\n", "")

    @commands.command(
        name=loc["pdf"]["name"],
        aliases=loc["pdf"]["aliases"],
        description=loc["pdf"]["description"]
    )
    async def pdf(self, ctx: Context, file_name: str=""):
        """Exports the game to a PDF"""

        assert ctx.guild

        # Start timer
        start_time = timer()

        # Get event loop
        loop = asyncio.get_running_loop()

        # Import game data
        asyncio.create_task(ctx.send(loc["pdf"]["CollectingData"]))
        try:
            await self.import_data(ctx)
        except KeyError:
            asyncio.create_task(ctx.send(loc["pdf"]["FailedImport"]))
            return

        # If data not found, tell user and quit
        if not ctx.game.start_time:
            asyncio.create_task(ctx.send(loc["pdf"]["MissingGameData"]))
            return

        # Create pdf object
        pdf = PDF(format="letter", unit="in")
        await loop.run_in_executor(None, pdf.set_auto_page_break, *(True, 1))

        # Add fonts
        await loop.run_in_executor(
            None, pdf.add_font, *("Built", "", str(BUILT_TITLING_RG), True)
        )
        await loop.run_in_executor(
            None, pdf.add_font, *("Built", "sb", str(BUILT_TITLING_SB), True)
        )
        await loop.run_in_executor(
            None, pdf.add_font, *("Built", "bd", str(BUILT_TITLING_BD), True)
        )
        await loop.run_in_executor(
            None, pdf.add_font, *("Abel", "", str(ABEL_REGULAR), True)
        )

        # Cover page
        await loop.run_in_executor(None, pdf.add_page)
        # Heading
        await loop.run_in_executor(
            None, self.heading,
            *(ctx, pdf, LOCALIZATION_DATA["title"],
              COVER_TITLE_FONT, "C", COVER_TITLE_Y)
        )

        # Poster
        poster = utils.get_image(dirs.POSTER_DIR, f"Alice-Briarwood-{ctx.game.alice}")
        await loop.run_in_executor(
            None, pdf.image,
            *(str(poster), COVER_POSTER_X,
              COVER_POSTER_Y, COVER_POSTER_WIDTH)
        )

        # Create list of player characters
        characters = ctx.game.active_chars()

        await ctx.send(loc["pdf"]["BuildingCharPages"])

        pm_channels = []
        for i, character in enumerate(characters):
            # Create pages for each character
            await loop.run_in_executor(
                None, self.generate_char_page, *(ctx, pdf, character)
            )

            # Create list of character pairs
            for j in range(i+1, len(characters)):
                pm_channels.append((character, characters[j]))

        await ctx.send(loc["pdf"]["RecreatingTimeline"])

        # Conclusions/timeline
        # TODO: either timeline will have to be async or it will also need
        # to be wrapped in loop.run_in_executor
        #
        # self.timeline(ctx, pdf)
        await loop.run_in_executor(None, self.conclusion_page, *(ctx, pdf))

        await ctx.send(loc["pdf"]["CollectingMessages"])

        # Group chat export
        pdf.add_page()
        await loop.run_in_executor(
            None, self.heading,
            *(ctx, pdf, loc["pdf"]["group-chat"], PM_TITLE_FONT, '',
              MESSAGES_TITLE_Y, MESSAGES_TITLE_TEXT_GAP)
        )
        await self.channel_export(ctx, pdf, ctx.text_channels[LOCALIZATION_DATA["channels"]["texts"]["group-chat"]])

        # Chat message exports
        for a, b in pm_channels:
            try:
                channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["texts"][f"{a}-{b}"]]
            except KeyError:
                # Fallback from older versions
                channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["texts"][f"pm-{a}-{b}"]]

            # Make sure channel has messages that will be counted
            empty = True
            async for message in channel.history(limit=None, oldest_first=True):
                line = utils.clean_message(ctx, message.clean_content)

                if line:
                    empty = False
                    break

            if not empty:
                title = f"{a.title()}/{b.title()}"
                pdf.add_page()
                await loop.run_in_executor(
                    None, self.heading,
                    *(ctx, pdf, title, PM_TITLE_FONT, '',
                      MESSAGES_TITLE_Y, MESSAGES_TITLE_TEXT_GAP)
                )

                await self.channel_export(ctx, pdf, channel)

        # Output the file
        if not file_name:
            file_name = ctx.guild.name

        out = (dirs.PDF_EXPORT_DIR / file_name).with_suffix(".pdf")
        pdf.output(str(out))

        end_time = timer()
        time = constants.TIMER_FORMAT % (end_time - start_time)
        print(f"PDF generated in {time} seconds.")

        await ctx.send(loc["pdf"]["PDFCreated"])

    def heading(self, ctx: Context, pdf: PDF, title: str, font,
                align='', y=None, gap: float = 0):
        """Add a heading to the current page"""

        pdf.set_font(*font)
        if y is not None:
            pdf.set_y(y)
        pdf.cell(0, 0, title, align=align)
        pdf.ln(gap)

    def generate_char_page(self, ctx: Context, pdf: PDF, character: str):
        """Creates a character page"""

        pdf.add_page()

        # Name at top left
        pdf.set_xy(CHAR_TITLE_X, CHAR_TITLE_Y)
        pdf.set_font(*CHAR_TITLE_FONT)

        title = "\n".join(cards.CHARACTERS[character].pdf_name_format)

        pdf.multi_cell(0, CHAR_TITLE_HEIGHT, title)

        # Character and motive cards
        card = utils.get_image(dirs.CHARACTER_IMAGE_DIR, character.split()[0])
        pdf.image(str(card), CHAR_CARD_LEFT, CHAR_CARD_TOP, CHAR_CARD_WIDTH)

        motive = ctx.game.motives[character]
        card = utils.get_image(dirs.MOTIVE_DIR, f"Motive-{motive}")
        pdf.image(str(card), CHAR_CARD_LEFT, MOTIVE_CARD_TOP, CHAR_CARD_WIDTH)

        # Clues
        current_y = CLUE_CARDS_TOP
        for clue in ctx.game.clue_assignments[character]:
            # Skip 90 and 10 clues
            if clue in (90, 10):
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
            card = utils.get_image(dirs.CLUE_DIR / str(clue), f"{clue}-{choice}")
            pdf.image(str(card), CLUE_CARD_LEFT, current_y, CLUE_CARD_WIDTH)

            # Suspect card
            if clue in ctx.game.suspects_drawn:
                suspect = ctx.game.suspects_drawn[clue]
                card = utils.get_image(dirs.SUSPECT_IMAGE_DIR, suspect)
            elif clue in ctx.game.locations_drawn:
                location = ctx.game.locations_drawn[clue]
                card = utils.get_image(dirs.LOCATION_IMAGE_DIR, location)

            pdf.image(str(card), SUSPECT_CARD_LEFT, current_y, CLUE_CARD_WIDTH)

            current_y += CLUE_CARD_HEIGHT + CLUE_CLUE_GAP

        # Voicemail
        pdf.set_font(*VOICEMAIL_TITLE_FONT)
        pdf.set_y(VOICEMAIL_TITLE_Y)
        pdf.cell(0, 0, VOICEMAIL_TITLE)
        pdf.set_font(*VOICEMAIL_FONT)
        pdf.set_y(VOICEMAIL_Y)
        pdf.multi_cell(0, VOICEMAIL_TEXT_LINE_HEIGHT,
                       ctx.game.voicemails[character])

    def conclusion_page(self, ctx: Context, pdf: PDF):
        """Create conclusions page based on 10 minute clue"""

        # Add title
        pdf.add_page()
        self.page_title(
            pdf, CONCLUSION_TITLE_Y, CONCLUSION_TITLE_FONT, CONCLUSION_TITLE
        )

        # Labels
        pdf.set_font(*CONCLUSION_LABEL_FONT)
        pdf.set_y(CONCLUSION_ROW1_LABEL_Y)

        pdf.set_x(CONCLUSION_CHAR_CARD_X - CONCLUSION_LABEL_OFFSET)
        label = loc["pdf"]["investigator"]
        width = pdf.get_string_width(label)
        pdf.cell(width, 0, label)

        pdf.set_x(CONCLUSION_CLUE_CARD_X - CONCLUSION_LABEL_OFFSET)
        label = loc["pdf"]["ending"]
        width = pdf.get_string_width(label)
        pdf.cell(width, 0, label)

        pdf.set_x(CONCLUSION_LOCATION_CARD_X - CONCLUSION_LABEL_OFFSET)
        label = loc["pdf"]["location"]
        width = pdf.get_string_width(label)
        pdf.cell(width, 0, label)

        # Row 2
        pdf.set_y(CONCLUSION_ROW2_LABEL_Y)

        pdf.set_x(CONCLUSION_CHAR_CARD_X - CONCLUSION_LABEL_OFFSET)
        label = loc["pdf"]["culprit"]
        if ctx.game.second_culprit:
            label = loc["pdf"]["culprit1"]
        width = pdf.get_string_width(label)
        pdf.cell(width, 0, label)

        if ctx.game.second_culprit:
            pdf.set_x(CONCLUSION_CLUE_CARD_X - CONCLUSION_LABEL_OFFSET)
            label = loc["pdf"]["culprit2"]
            width = pdf.get_string_width(label)
            pdf.cell(width, 0, label)

        # Images
        # Add character card
        assert ctx.game.ten_char
        card = filepaths.MASTER_PATHS[ctx.game.ten_char]
        pdf.image(str(card), CONCLUSION_CHAR_CARD_X,
                  CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add clue card
        card = utils.get_image(dirs.CLUE_DIR / "10", f"10-{ctx.game.picked_clues[10]}")
        pdf.image(str(card), CONCLUSION_CLUE_CARD_X,
                  CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add location card
        card = filepaths.MASTER_PATHS[ctx.game.locations_drawn[20]]
        pdf.image(str(card), CONCLUSION_LOCATION_CARD_X,
                  CONCLUSION_ROW1_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add first suspect card
        card = filepaths.MASTER_PATHS[ctx.game.suspects_drawn[30]]
        pdf.image(str(card), CONCLUSION_SUSPECT_CARD_X,
                  CONCLUSION_ROW2_IMAGE_Y, CONCLUSION_CARD_WIDTH)

        # Add second suspect card
        if ctx.game.second_culprit:
            card = filepaths.MASTER_PATHS[ctx.game.second_culprit]
            pdf.image(str(card), CONCLUSION_CLUE_CARD_X,
                      CONCLUSION_ROW2_IMAGE_Y, CONCLUSION_CARD_WIDTH)

    def timeline(self, ctx: Context, pdf: PDF):
        """Adds timeline pages to PDf"""

        pdf.add_page()
        self.page_title(
            pdf, TIMELINE_TITLE_Y, TIMELINE_TITLE_FONT, TIMELINE_TITLE
        )

    def page_title(self, pdf: PDF, y: float, font, text: str):
        """Add title to current page"""

        pdf.set_y(y)
        pdf.set_font(*font)
        pdf.cell(0, 0, text)

    async def channel_export(self, ctx: Context, pdf: PDF, channel: discord.TextChannel):
        """
        Takes all messages from a text channel and adds them
        to the current page of the PDF object
        """

        # Get event loop
        loop = asyncio.get_running_loop()

        pdf.set_font(*PM_FONT)
        async for message in channel.history(limit=None, oldest_first=True):
            assert isinstance(message.author, discord.Member)

            # Name
            author = message.author.roles[1].name

            # Remove emojis and out of character parts
            line = utils.clean_message(ctx, message.clean_content)

            # If string is empty after cleaning, skip
            if line == "":
                continue

            # If message looks like a command attempt, ignore it
            if utils.is_command(line):
                continue

            line = f"{author}: {line}"

            # Time remaining
            if ctx.game.start_time is None:
                return
            delta = message.created_at - ctx.game.start_time
            change = delta.seconds
            time = gamedata.GAME_LENGTH - change
            if time >= 0:
                # Don't display timestamp if after game has ended
                stamp = f"({utils.time_string(time)})"
                line += f" {stamp}"

            await loop.run_in_executor(None, pdf.multi_cell,
                                       *(0, MESSAGES_LINE_HEIGHT, line))

    @commands.command(
        name=loc["upload"]["name"],
        aliases=loc["upload"]["aliases"],
        description=loc["upload"]["description"]
    )
    async def upload(self, ctx: Context, file_name: str=""):
        """Uploads a file and prints out the download url"""

        assert ctx.guild

        if not file_name:
            file_name = ctx.guild.name
        path = (dirs.PDF_EXPORT_DIR / file_name).with_suffix(".pdf")
        url = utils.upload_file(path)
        await ctx.send(url)

    @commands.command(hidden=True)
    async def txt(self, ctx: Context):
        """Gets all messages from a guild and writes to a .txt file"""

        # TODO: Make this cleaner
        # Hidden from users until then

        asyncio.create_task(ctx.send("Downloading..."))
        # make folder for messages
        message_dir = dirs.TEXT_EXPORT_DIR / ctx.guild.name
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
        zip_file = WHITE_RABBIT_DIR / f"{ctx.guild.name} Messages.zip"
        shutil.make_archive(
            zip_file.with_suffix(""),
            "zip", message_dir,
        )
        asyncio.create_task(ctx.send(file=discord.File(zip_file)))

        # Delete files
        shutil.rmtree(message_dir)
        zip_file.unlink()


async def setup(bot: Bot):
    await bot.add_cog(Export(bot))
