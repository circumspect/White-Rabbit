************
Localization
************

To change the language the bot runs in, modify the ``LANGUAGE`` key in the
``.env`` file. A table of languages with their key values is show below:

+---------------+--------+--------------------------------------+--------------+
| LANGUAGE      | Code   | Discord Server Template              | Status       |
+===============+========+======================================+==============+
| English       | en     | https://discord.new/YD7aEUr8AdBQ     | Complete     |
+---------------+--------+--------------------------------------+--------------+
| French        | fr     |                                      | Incomplete   |
+---------------+--------+--------------------------------------+--------------+

If you would like to contribute translations, fork the repository, copy
``english.json`` in the ``localization`` folder, translate the values
(leave the keys intact), and open a pull request. For an example, see the
(incomplete) French translation in ``french.json``. Note that changing the
names of the Discord server channels in the .json file will require making a
new Discord template.
