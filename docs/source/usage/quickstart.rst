****************
Quickstart Guide
****************

This guide assumes familiarity with the rules and gameplay of Alice is Missing. To purchase a PDF copy of the game, including the rulebook, `click here <https://www.drivethrurpg.com/product/321387/Alice-Is-Missing-A-Silent-Roleplaying-Game>`_.

Playing the game
================

Running the bot
---------------

To run the bot, open a shell window and enter the following:

.. code:: console

   $ python3 /path/to/src

Where /path/to/src is the path to the src folder in the bot's root directory.


Game setup
----------

For setup, join the voice channel and have players join you.

.. note::
   All bot commands should be entered into ``#bot-channel``. The bot will not respond to commands in other channels.

To begin setting up the game, type ``!init`` into the channel titled ``#bot-channel`` in your server. The bot should begin sending cards out to their respective channels. Have players navigate to ``player-resources``. Read the introduction card out loud, and introduce Alice from the poster. Now, have players navigate to ``#character-cards`` and introduce the five characters with their brief taglines (directly underneath their names on the cards). Tell players you will be playing as Charlie Barnes, and have them pick the characters they would like to play amongst themselves. To claim a character role, use ``!claim <Player>``, e.g. ``!claim Charlie``. Once all players have claimed their character roles, run ``!setup_clues`` to assign clue times to each player.


Starting the game
-----------------

To start the game, run ``!start``.


.. note::
   For a list of all available bot commands, use ``!help``