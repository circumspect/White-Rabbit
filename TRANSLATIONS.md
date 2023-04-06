# Translations

If you would like to contribute translations, fork the repository, copy
`en.json` in the `localization` folder, translate the values (leave
the keys intact), and open a pull request. For an example, see the French
translation in `fr.json`. Note that changing the names of the channels
means you will need to run `!server_setup` so that the bot can generate
channels with the correct names and permissions.

You can also submit translations of the cards used in the game by copying the
`templates` folder in `resources/images` and matching the new folder name to
the key used for the language, then editing the `.kra` file and exporting the
translated cards **AS PNG FILES**. The bot will default to the English
versions of any cards it can't find. To edit the files, you will need
[Krita](https://krita.org/en/), an open source tool for creating and modifying
images. Not all of the cards currently have templates,
so feel free to submit those as well!
