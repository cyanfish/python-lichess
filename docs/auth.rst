Authentication
==========================================

Authentication lets you download games at a faster rate and access private data.

The simplest way to authenticate is to create an OAuth access token on `lichess.org <https://lichess.org/account/oauth/token>`_, and use the :data:`auth` parameter like so:

>>> import lichess.api
>>>
>>> games = lichess.api.user_games('cyanfish', max=100, auth='your-token-here')

You can also authenticate using your username and password (but please, try and avoid this):

>>> import lichess.api
>>>
>>> cookie = lichess.api.login('cyanfish', 'this-is-not-my-real-password')
>>> games = lichess.api.user_games('cyanfish', max=100, auth=cookie)

.. automodule:: lichess.auth
    :members: OAuthToken, Cookie, EMPTY
