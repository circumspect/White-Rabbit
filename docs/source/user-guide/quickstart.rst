****************
Quickstart Guide
****************

This guide assumes familiarity with the rules and gameplay of Alice is
Missing. To purchase a PDF copy of the game, including the rulebook,
`click here <https://www.drivethrurpg.com/product/321387/Alice-Is-Missing-A-Silent-Roleplaying-Game>`_.

If you have not yet installed the bot, see :doc:`installation`

Playing the game
================

Running the bot
---------------

To run the bot, open a shell window and enter the following:

.. code:: console

   $ python /path/to/src

Where ``/path/to/src`` is the path to the src folder in the bot's root
directory.


Game setup
----------

For setup, join the voice channel and have players join you.

.. note::
   All bot commands should be entered into ``#bot-channel``. The bot will not respond to commands in other channels.

To begin setting up the game, type ``!init`` into the channel titled
``#bot-channel`` in your server. The bot should begin sending cards out to
their respective channels. Have players navigate to ``player-resources``.
Read the introduction card out loud, and introduce Alice from the poster.
Now, have players navigate to ``#character-cards`` and introduce the five
characters with their brief taglines (directly underneath their names on the
cards). Tell players you will be playing as Charlie Barnes, and have them
pick the characters they would like to play amongst themselves. To claim a
character role, use ``!claim <Player>``, e.g. ``!claim Charlie``.


.. note::
   The bot cannot change the server owner's nickname because of a limitation
   set by Discord. If the server owner is playing, they should set their own
   nickname to match their character.

Once all players have claimed their character roles, run ``!setup_clues`` to
assign clue times to each player. Continue following the checklist at the top
of ``#charlie-clues`` to explain the mechanics of the game to the players.
Remember to keep Charlie's background (also at the top of ``#charlie-clues``)
in mind when describing your character.


Starting the game
-----------------

To start the game, run ``!start``. The bot will automatically send clues to
the appropriate clues channel along with the corresponding suspect/location.
The only other command that needs to be run after the game has begun is using
the 10 command to assign the 10 minute clue card to the player who is going
to Alice's location near the end of the game, e.g. ``!10 Dakota``. Should a
player need to draw a searching card, have them run ``!search``.

.. note::
   Some clues may ask players to flip a coin. The bot will generate this flip
   automatically and send the result at the appropriate times. There is no
   need for players to flip a coin themselves.


Other settings
--------------

The bot has a few gameplay-related settings available, including displaying a
timer and running in manual mode. For more information on these, see
:doc:`settings`

.. note::
   For a list of all available bot commands, use ``!help``


End of game
-----------

At the end of the game, you may wish to allow your players to see the other
characters' clues and messages. To do this, run ``!show_all``. (Note that this
command is only available to those with admin permissions on the server.)

You can also export the game content to a PDF using ``!pdf``. This will create
a folder titled "exports" in the bot's root directory, where you can find the
.pdf file.
