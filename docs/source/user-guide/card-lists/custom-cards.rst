********************************************
Expansions, Playsets, and Custom Cards
********************************************

.. note::
    This page is intended for those who wish to define their own sets of
    cards, or to use a custom list of expansions. If you only want to run
    a game using the base set, follow the instructions in :doc:`/user-guide/quickstart`.
    If you want to run a game using all officially released expansions, see
    :doc:`official`.


Playsets
====================

Playsets are the main tool used for managing which cards the White Rabbit
will use during a particular game. They can be thought of as a list of
expansions, combined with some metadata. If you already have an expansion
of custom cards, you can add it to your game by simply defining a new playset.
The playset for the set of all officially released expansions
looks as follows (see ``official.yaml``)::

    starting-player: charlie

    expansions:
        - base
        - silent-falls

Playsets are stored in the folder ``card_lists/playsets``, in the YAML format.
Below is the list of fields a playset can have:


starting-player
-----

Required. This is the character that will receive the 90 minute clue card.

expansions
-----

Required. This is the list of expansions to pull cards from.
Names can include subfolders, e.g., ``my_custom_cards/wonderland``.



Expansions
====================

Expansions allow defining custom cards, and are stored in
``card_lists/expansions``. See ``base.yaml`` for an example.
