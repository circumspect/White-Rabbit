************
Localization
************

To change the language the bot runs in, modify the ``WHITE_RABBIT_LANGUAGE`` key in the
``.env`` file. A table of languages with their key values is show below:

.. csv-table::
   :file: ./localizations.csv
   :header-rows: 1

.. _circumspect: https://github.com/circumspect
.. _Ylkhana: https://github.com/Ylkhana
.. _Gabbalo: https://github.com/Gabbalo
.. _d-beezee: https://github.com/d-beezee
.. _wishmerhill: https://github.com/wishmerhill


If you would like to contribute translations, fork the repository, copy
``en.json`` in the ``localization`` folder, translate the values
(leave the keys intact), and open a pull request. For an example, see the
French translation in ``fr.json``. Note that changing the names of the
Discord server channels in the .json file will require either making a new
Discord template, or running ``!server_setup`` before play.
