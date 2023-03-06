***************
Expansions
***************

By default, the White Rabbit will start a game with the base set of
Alice is Missing cards. If you would like to start a game using the
cards from all officially released expansions, add the following
environment variable (see :doc:`env` for details):

`WHITE_RABBIT_PLAYSET=official`

.. note::
    The default server template will not work with character cards not
    included in the base set! When changing playsets, make sure to run the
    ``!server_setup`` command to update your server


Below is the list of all official expansions that can be used in a playset:

* base
* silent-falls (coming soon!)


If you would like to define your own custom expansions and/or playsets,
see :doc:`custom-cards`.
