***********
Debug Tools
***********

This page documents commands which may be useful for debugging and bot development.


Enabling dev commands
=====================

To give yourself access to the debug commands, set the ``WHITE_RABBIT_DEBUG``
environment variable to true.


Setting the bot's game speed
============================

When debugging the bot, you may find it helpful to speed up the bot to avoid
having to wait 90 minutes (the length of the game) for the bot to finish.
This can be done using ``!speed``. For example, the following sets the bot to
run at 3x speed:

.. code::

    !speed 3

The minimum speed is 1, and the maximum is 30. Note that setting a speed
higher than 1 will cause the bot to change the gap between timer messages to
60 seconds to avoid bumping into the Discord rate limit. Should you wish to
change this, simply set the timer frequency using ``!timer`` after running
``!speed``. Also, at higher speeds the timer messages being printed out in
the ``bot-commands`` channel may lag behind the bot's internal timer (and
thus the clues), so the best way to ensure the bot behaves as expected after
making changes is to do a test run at normal speed.


Shutting Down the Bot
=====================

You can shut down the bot through Discord using the ``!quit`` command. Note
that this will cancel all in progress games on all servers the bot is
currently running in, and will not save progress.
