python-lichess: a client for the lichess.org API
================================================

This is a client library for the `lichess.org <https://lichess.org>`_ `API <https://github.com/ornicar/lila#http-api>`_. It is designed to be:

* Easy to use

* Customizable when you need it

* Adaptable to API changes

* Easy to `integrate <pgn.html#lichess.pgn.io_from_game>`_ with `python-chess <https://github.com/niklasf/python-chess>`_

Have a look at some short examples. For more, check out the `full documentation <http://python-lichess.readthedocs.io/>`_.

Getting a user's rating:

>>> import lichess.api
>>> 
>>> user = lichess.api.user('thibault')
>>> print(user['perfs']['blitz']['rating'])
1617

Saving a PGN of the user's last 200 games:

>>> import lichess.api
>>> import lichess.pgn
>>> import itertools
>>> 
>>> games = lichess.api.user_games('thibault', with_moves=1)
>>> last_200 = itertools.islice(games, 200)
>>> lichess.pgn.save_games(last_200, 'last200.pgn')

Integrating with `python-chess <https://github.com/niklasf/python-chess>`_:

>>> import lichess.api
>>> import lichess.pgn
>>> import chess.pgn
>>> 
>>> api_game = lichess.api.game('Qa7FJNk2', with_moves=1)
>>> game = chess.pgn.read_game(lichess.pgn.io_from_game(api_game))
>>> print(game.end().board())
. . k . R b r .
. p p r . N p .
p . . . . . . p
. . . . . . . .
. . . p . . . .
P . . P . . . P
. P P . . P P .
. . K R . . . .
