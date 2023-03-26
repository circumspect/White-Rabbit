**************
Admin Commands
**************

This page documents the commands available for admins of servers in which
the bot is running. Users who do not have admin permissions in the Discord
server will not be able to run these commands.


Channel Reveals
===============

At the end of the game, you may wish to allow your players to see the other
characters' clues and messages. To do this, run ``!show_all``.


Resetting the server
====================

You can wipe all messages from the server using ``!wipe``. This is useful
if, for example, you called ``!init`` twice and now have two copies of each
character and motive card in the clues channels. Note that after running this
you will have to start setup again from the beginning.

``!wipe`` accepts three different kinds of optional arguments, listed below:

- Text channel names or tags, e.g., ``discussion`` or ``#bot-channel``
- Names of channel categories, e.g., ``Texts``
- Integer indexes for channel categories, from top to bottom, starting with 0. By default this will be:
    - 0: ``General/OOC``
    - 1: ``The Game``
    - 2: ``Texts``

If given a partial channel/category name, such as ``gen``, the bot will
convert it to lowercase before attempting to find a category whose lowercased
name contains the given substring. If this fails, it will then attempt the
same with text channels. If neither is found, the command will abort. The
command will also abort if given an integer index not in the range [0, n-1],
where n is the number of channel categories.

The above can be mix and matched when calling ``!wipe``. For example,
``!wipe #bot-channel 2`` will wipe the bot channel and all of the text message
channels.

``!reset_perms`` sets the permissions for each channel back to the default.
This is mainly used if ``!show_all`` was called by accident.

To wipe all messages and reset channel permissions in one step,
run ``!reset``. The server will then be the same as if you made a new server
from the template (unless you changed channel permissions by hand). The main
purpose of this function is for clearing a server when testing the bot. If
starting a new game, consider making a new server and simply adding the bot
again.
