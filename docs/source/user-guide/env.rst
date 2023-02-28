*********************
Environment Variables
*********************

The following is a list of environment variables that the bot can use.
Variables in the environment take precedence over variables found in
the ``.env`` file. To use the ``.env`` file, use the format
``VARNAME=VALUE``, (e.g., ``WHITE_RABBIT_TOKEN=123456789``) with one value per line.


WHITE_RABBIT_TOKEN
-----

The Discord token for the bot. Required.


WHITE_RABBIT_LANGUAGE
-----------

The localization to be used by the bot. Defaults to ``en``. For a list of
supported languages, see :doc:`localization`.


WHITE_RABBIT_PLAYSET
------

The playset to use for the bot. Defaults to ``base``. For details, see
:doc:`card-lists/official`.


WHITE_RABBIT_USE_LOCAL_IMAGES
--------------------

Defaults to ``false``. If true, the bot will upload the images from its
``resources`` folder instead of linking to the images on Github. Mainly
intended for development or for custom cards
(see :doc:`card-lists/custom-cards`),
as it is much faster for the bot to send a link
and allow Discord to render it.
