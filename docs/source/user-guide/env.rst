*********************
Environment Variables
*********************

The following is a list of environment variables that the bot can use.
Variables in the environment take precedence over variables found in
the ``.env`` file. To use the ``.env`` file, use the format
``VARNAME=VALUE``, (e.g., ``TOKEN=123456789``) with one value per line.


TOKEN
-----

The Discord token for the bot. Required.


LANGUAGE
-----------

The localization to be used by the bot. Defaults to ``en``. For a list of
supported languages, see :doc:`localization`.


USE_LOCAL_IMAGES
--------------------

Defaults to ``false``. If true, the bot will upload the images from its
``resources`` folder instead of linking to the images on Github. Mainly
intended for development, as it is much faster for the bot to send a link
and allow Discord to render it.
