************
Installation
************

Download the zip from github `here <https://github.com/circumspect/White-Rabbit/archive/master.zip>`_ and extract the files to a directory of your choice. Install any missing libraries from ``requirements.txt`` using pip.

Create a new Discord server using the following template: https://discord.new/YD7aEUr8AdBQ and name it Alice is Missing.

Next, create a new Discord bot as follows:

Log in to the `Discord Developer portal <https://discord.com/developers/applications>`_. Click on "New Application" and name it "The White Rabbit". Then click on the Bot tab and click "Add Bot". You may optionally add the bot icon here. Copy the token using the button next to the icon. Create a file named ``token.txt`` in the bot's root directory and paste the token in. After creating the token file, navigate to the "Bot" tab. Under "Privileged Gateway Intents", set the toggle for "Server Members Intent" to true. Then go to the OAuth2 tab and scroll to the bottom. Under "Scopes", check the box labeled ``bot``. Scroll down to "Bot Permissions" and check the box labeled "Administrator". Scroll back up to "Scopes", copy the link at the bottom of the box and open it in a new tab. Follow the instructions to add the bot to the server you previously created.

Finally, open the Discord app, find your server, and open the server role settings (click on the server name -> Server Settings -> Roles). Click and drag the "The White Rabbit" role to the top of the list of roles and click "Save Changes". Close the settings and you're done with setup!
