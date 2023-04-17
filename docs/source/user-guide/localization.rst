************
Localization
************

To change the language the bot runs in, modify the ``WHITE_RABBIT_LANGUAGE`` key in the
``.env`` file. For a list of supported languages and the completeness of their
translations, see `this issue`_.

.. _this issue: https://github.com/circumspect/White-Rabbit/issues/156

If you would like to contribute translations, fork the repository, copy
``en.json`` in the ``localization`` folder, translate the values
(leave the keys intact), and open a pull request. For an example, see the
French translation in ``fr.json``. Note that changing the names of the
Discord server channels in the .json file will require running
``!server_setup`` before play.
