# The White Rabbit

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/circumspect/White-Rabbit/login-test.yml?branch=main)
[![Documentation Status](https://readthedocs.org/projects/white-rabbit/badge/?version=latest)](https://white-rabbit.readthedocs.io/en/latest/?badge=latest)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/circumspect/White-Rabbit)](https://github.com/circumspect/White-Rabbit/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/circumspect/white-rabbit?label=Docker%20Hub)](https://hub.docker.com/r/circumspect/white-rabbit)
[![License](https://img.shields.io/github/license/circumspect/White-Rabbit)](https://github.com/circumspect/White-Rabbit/blob/main/LICENSE)

A Discord bot for Alice is Missing. Server template: <https://discord.new/SfcBdbyhGMmR>.
This is a fan-made project which is not affiliated in any way with the creators of Alice is Missing.
Game and all Alice is Missing images are property of
[Hunters Entertainment](https://www.huntersentertainment.com/alice-is-missing).
If you haven't already, please go buy a copy of the game to support them (and
to get a copy of the rulebook). Code and documentation are licensed under the
AGPLv3.

Documentation can be found [here](https://white-rabbit.readthedocs.io/).

## Translations Wanted

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

## Contributors ✨

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors)
specification. Contributions of any kind welcome!

Built with help from these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/circumspect"><img src="https://avatars.githubusercontent.com/u/40770208?v=4?s=100" width="100px;" alt="circumspect"/><br /><sub><b>circumspect</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=circumspect" title="Code">💻</a> <a href="https://github.com/circumspect/White-Rabbit/commits?author=circumspect" title="Documentation">📖</a> <a href="#design-circumspect" title="Design">🎨</a> <a href="#maintenance-circumspect" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Creonalia"><img src="https://avatars.githubusercontent.com/u/52385967?v=4?s=100" width="100px;" alt="Creonalia"/><br /><sub><b>Creonalia</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=Creonalia" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://skylerberg.com"><img src="https://avatars.githubusercontent.com/u/4156131?v=4?s=100" width="100px;" alt="Skyler Berg"/><br /><sub><b>Skyler Berg</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=skylerberg" title="Code">💻</a> <a href="https://github.com/circumspect/White-Rabbit/commits?author=skylerberg" title="Documentation">📖</a> <a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3Askylerberg" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://0x99.net"><img src="https://avatars.githubusercontent.com/u/8868033?v=4?s=100" width="100px;" alt="Tanner Stephens"/><br /><sub><b>Tanner Stephens</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=tannerstephens" title="Code">💻</a> <a href="https://github.com/circumspect/White-Rabbit/commits?author=tannerstephens" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ylkhana"><img src="https://avatars.githubusercontent.com/u/48254532?v=4?s=100" width="100px;" alt="Ylkhana"/><br /><sub><b>Ylkhana</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=Ylkhana" title="Code">💻</a> <a href="#translation-Ylkhana" title="Translation">🌍</a> <a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3AYlkhana" title="Bug reports">🐛</a> <a href="#design-Ylkhana" title="Design">🎨</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/theo-ardouin"><img src="https://avatars.githubusercontent.com/u/13322753?v=4?s=100" width="100px;" alt="Théo Ardouin"/><br /><sub><b>Théo Ardouin</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=theo-ardouin" title="Code">💻</a> <a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3Atheo-ardouin" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://loh.re"><img src="https://avatars.githubusercontent.com/u/5897819?v=4?s=100" width="100px;" alt="Gabriel"/><br /><sub><b>Gabriel</b></sub></a><br /><a href="#translation-Gabbalo" title="Translation">🌍</a> <a href="#userTesting-Gabbalo" title="User Testing">📓</a> <a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3AGabbalo" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Zanaku"><img src="https://avatars.githubusercontent.com/u/1145197?v=4?s=100" width="100px;" alt="Tom Whiteley"/><br /><sub><b>Tom Whiteley</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3AZanaku" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://pipejakob.com"><img src="https://avatars.githubusercontent.com/u/1605981?v=4?s=100" width="100px;" alt="Jacob Beacham"/><br /><sub><b>Jacob Beacham</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=pipejakob" title="Code">💻</a> <a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3Apipejakob" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ghuldrigan"><img src="https://avatars.githubusercontent.com/u/28635092?v=4?s=100" width="100px;" alt="Ghuldrigan"/><br /><sub><b>Ghuldrigan</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3AGhuldrigan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.nousefornames.it"><img src="https://avatars.githubusercontent.com/u/210835?v=4?s=100" width="100px;" alt="Alberto"/><br /><sub><b>Alberto</b></sub></a><br /><a href="#translation-wishmerhill" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/d-beezee"><img src="https://avatars.githubusercontent.com/u/59012086?v=4?s=100" width="100px;" alt="d-beezee"/><br /><sub><b>d-beezee</b></sub></a><br /><a href="#translation-d-beezee" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Leujii"><img src="https://avatars.githubusercontent.com/u/126162473?v=4?s=100" width="100px;" alt="Leujii"/><br /><sub><b>Leujii</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3ALeujii" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Sinesthesyc"><img src="https://avatars.githubusercontent.com/u/126390834?v=4?s=100" width="100px;" alt="Sinesthesyc"/><br /><sub><b>Sinesthesyc</b></sub></a><br /><a href="#translation-Sinesthesyc" title="Translation">🌍</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dracek1458"><img src="https://avatars.githubusercontent.com/u/32167387?v=4?s=100" width="100px;" alt="dracek1458"/><br /><sub><b>dracek1458</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/issues?q=author%3Adracek1458" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/PokePango"><img src="https://avatars.githubusercontent.com/u/34710204?v=4?s=100" width="100px;" alt="PokePango"/><br /><sub><b>PokePango</b></sub></a><br /><a href="https://github.com/circumspect/White-Rabbit/commits?author=PokePango" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
