************
Installation
************

Default Installation
====================

.. note::
  Make sure you are using at least Python 3.7. The bot will not be able to run
  otherwise.

Download the source zip from Github `here <https://github.com/circumspect/White-Rabbit/releases/>`_
and extract the files to a directory of your choice. Install any missing
libraries from ``requirements.txt`` using pip (i.e., ``pip install -r requirements.txt``).

Create a new Discord server using the following template:
https://discord.new/SfcBdbyhGMmR and name it however you like.

.. note::
   If you wish to use the bot in a different language, you must use the server
   template corresponding to that language. See :doc:`localization` for a list
   of supported languages and Discord server templates.

Next, create a new Discord bot as follows:

- Log in to the `Discord Developer portal <https://discord.com/developers/applications>`_.
- Click on "New Application" and name it "The White Rabbit".
- Click on the Bot tab and click "Add Bot".

  - You may optionally add the bot icon here.

- Copy the token using the button next to the icon.
- Open the file named ``example.env`` in the bot's root directory and paste
  the token in.
- Rename this file to ``.env``.
- Go to the Bot tab.

  - Under "Privileged Gateway Intents", set all of the toggles to true and
    click "Save Changes".

- Go to the OAuth2 tab and scroll to the bottom.

  - Under "Scopes", check the box labeled ``bot``.
  - Scroll down to "Bot Permissions" and check the box labeled
    "Administrator".
  - Scroll back up to "Scopes", copy the link at the bottom of the box and
    open it in a new tab.
  - Follow the instructions to add the bot to the server you previously
    created.

- Finally, open the Discord app, find your server, and open the server role
  settings (click on the server name -> Server Settings -> Roles).
- Click and drag the "The White Rabbit" role to the top of the list of roles
  and click "Save Changes".
- Close the settings and you're done with setup!


Optional Settings
===================

Some bot settings, such as language, can be set through the use of optional
environment variables. See :doc:`env` for a full list.


Docker Installation
===================

Follow the Discord application setup above, skipping the steps relating to
the ``.env`` file.

Deploy the Docker container as follows, replacing ``YOUR_TOKEN_GOES_HERE``
with the Discord token obtained above.

`List of Docker tags <https://hub.docker.com/r/circumspect/white-rabbit/tags>`_
(version numbers are the same as Github releases).

.. code::

  docker run -d \
    --name=white-rabbit \
    --env WHITE_RABBIT_TOKEN=YOUR_TOKEN_GOES_HERE \
    --restart unless-stopped \
    circumspect/white-rabbit

Optional Environment Variables
------------------------------

You may set additional optional environment variables through Docker using
the `--env` option, e.g., ``--env WHITE_RABBIT_LANGUAGE=fr``.


Heroku Installation
===================

Follow the Discord application setup above, skipping the steps relating to
the `.env` file. Use the default Python buildpack. Make sure to set the
token and any other desired environment variables as necessary.
