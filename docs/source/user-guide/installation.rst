************
Installation
************

Download the source zip from Github `here <https://github.com/circumspect/White-Rabbit/releases/>`_ and extract the files to a directory of your choice. Install any missing libraries from ``requirements.txt`` using pip.

Create a new Discord server using the following template: https://discord.new/YD7aEUr8AdBQ and name it Alice is Missing.

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

  - Under "Privileged Gateway Intents", set the toggle for "Server Members
    Intent" to true and click "Save Changes".

- Go to the OAuth2 tab and scroll to the bottom.

  - Under "Scopes", check the box labeled ``bot``.
  - Scroll down to "Bot Permissions" and check the box labeled
    "Administrator".
  - Scroll back up to "Scopes", copy the link at the bottom of the box and
    open it in a new tab.
  - Follow the instructions to add the bot to the server you previously
    created.

- Finally, open the Discord app, find your server, and open the server role settings (click on the server name -> Server Settings -> Roles).
- Click and drag the "The White Rabbit" role to the top of the list of roles
  and click "Save Changes".
- Close the settings and you're done with setup!


Docker Installation
===================

Follow the Discord application setup above, don't worry about updating
the .env file though

Deploy the Docker container as follows, replacing ``YOUR_TOKEN_GOES_HERE``
with the discord token obtained above

`List of Docker tags <https://hub.docker.com/r/circumspect/white-rabbit/tags>`_ (version numbers are the same as Github releases).

.. code::

  docker run -d \
    --name=white-rabbit \
    --env TOKEN=YOUR_TOKEN_GOES_HERE \
    --restart unless-stopped \
    circumspect/white-rabbit


Optional Environment Variables
------------------------------

You may set additional optional environment variables through Docker,
as listed below:

+---------------+--------------------------------------+-----------------------+
| Variable Name | Usage                                | Example               |
+===============+======================================+=======================+
| LANGUAGE      | Sets the localization, default: en   | ``--env LANGUAGE=fr`` |
+---------------+--------------------------------------+-----------------------+
| DEV_ID        | Gives debug command access to the ID | ``--env DEV_ID=1234`` |
+---------------+--------------------------------------+-----------------------+


Heroku Installation
===================

The bot can be installed as a Heroku app, however note that a free dyno will
likely not be sufficient for the bot to run the game. The bot will log in
and respond to the ``!help`` command, but will have trouble sending images.
It should work with a paid dyno, but I have not tested it. To install,
simply use the default Python buildpack.
