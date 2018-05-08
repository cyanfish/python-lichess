python-lichess: a client for the lichess.org API
================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents
   
   api
   format
   auth
   pgn
   api-config

Introduction
------------

This is a client library for the `lichess.org <https://lichess.org>`_ `API <https://lichess.org/api>`_. It is designed to be:

* Easy to use

* Customizable when you need it

* Adaptable to API changes

* Easy to `integrate <format.html#lichess.format.PYCHESS>`_ with `python-chess <https://github.com/niklasf/python-chess>`_

Have a look at some short examples. For more, check out the full doc in the table of contents.

Getting a user's rating:

>>> import lichess.api
>>> 
>>> user = lichess.api.user('thibault')
>>> print(user['perfs']['blitz']['rating'])
1617

Checking who's online and playing:

>>> import lichess.api
>>>
>>> users = list(lichess.api.users_status(['thibault', 'cyanfish']))
>>> online = [u['id'] for u in users if u.get('online')]
>>> playing = [u['id'] for u in users if u.get('playing')]
>>> print(online, playing)
['thibault', 'cyanfish'] ['cyanfish']

Saving a PGN of a user's last 200 games:

>>> import lichess.api
>>> from lichess.format import SINGLE_PGN
>>> 
>>> pgn = lichess.api.user_games('thibault', max=200, format=SINGLE_PGN)
>>> with open('last200.pgn', 'w') as f:
>>>    f.write(pgn)

Integrating with `python-chess <https://github.com/niklasf/python-chess>`_:

>>> import lichess.api
>>> from lichess.format import PYCHESS
>>> 
>>> game = lichess.api.game('Qa7FJNk2', format=PYCHESS)
>>> print(game.end().board())
. . k . R b r .
. p p r . N p .
p . . . . . . p
. . . . . . . .
. . . p . . . .
P . . P . . . P
. P P . . P P .
. . K R . . . .

Installing
----------

::

    pip install python-lichess
