**************
Admin Commands
**************

This page documents the commands available for admins of servers in which the bot is running. Users who do not have admin permissions in the discord server will not be able to run these commands.

Channel Reveals
===============

At the end of the game, you may wish to allow your players to see the other characters' clues and messages. To do this, run ``!show_all``. (Note that this command is only available to those with admin permissions on the server.)

Resetting the server
====================

You can wipe all messages from the server using ``!wipe``. This is useful if, for example, you called ``!init`` twice and now have two copies of each character and motive card in the clues channels. Note that this will also clear any existing game data.

``!reset_perms`` sets the permissions for each channel back to the default. This is mainly used if ``!show_all`` was called by accident.

To wipe all messages and reset channel permissions in one step, run ``!reset``. The server will then be the same as if you made a new server from the template (unless you changed channel permissions by hand). The main purpose of this function is for clearing a server when testing the bot. If starting a new game, consider making a new server and simply adding the bot again.
