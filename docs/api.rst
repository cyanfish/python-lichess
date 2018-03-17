API Methods
==========================================

The module :mod:`lichess.api` provides thin wrappers around the `lichess API <https://github.com/ornicar/lila#http-api>`_.

In addition to the API parameters, each function takes an optional :data:`client` argument. See :doc:`api-config` for more information.

By default, paging is handled automatically by a returned generator. If you want to handle paging manually, append :data:`_page` to the name of a function that returns a generator.
For example, :data:`~lichess.api.user_games` becomes :data:`~lichess.api.user_games_page`.

.. automodule:: lichess.api
    :members: user, users_by_team, users_by_ids, users_status, user_games, user_activity, games_between, games_by_team, game, games_by_ids, tournaments, tournament, tournament_standings, tv_channels
