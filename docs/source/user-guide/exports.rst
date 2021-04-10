*******
Exports
*******

PDF Exports
===========

The White Rabbit supports exporting game data to a PDF file.
To do so, simply run ``!pdf`` at any point after the game has ended.
This feature works even if the bot was not present during the game and
was added later, as long as the channels have the same names as those in
the template and the filenames of the images match the bot's references.
However, if any of the players leave the server or no longer have their
nickname/role from the game, the PDF output will be incorrect or fail. The
file will be created on the computer running the bot in the ``exports``
folder in the bot's root directory. Note that because Discord limits file
uploads to 8MB and the generated files are ~25MB in size, there is no way
for the bot to send the PDF files directly via Discord.

The bot will also remove all emojis from messages before adding them to the
PDF, due to font limitations.


Sharing Files
=============

The ``!upload`` command will upload your PDF file to a temporary file hosting
site and reply with a link to download the file. The file hosting service is
unaffiliated with the White Rabbit and may or may not be secure.
