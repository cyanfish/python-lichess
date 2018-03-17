API Methods
==========================================

The module :mod:`lichess.api` provides thin wrappers around the `lichess API <https://github.com/ornicar/lila#http-api>`_.

In addition to the API parameters, each function takes an optional :data:`client` argument. See :doc:`api-config` for more information.

.. automodule:: lichess.api
    :members: user, users_by_team, users_by_team_page, users_by_ids, users_by_ids_page, users_status, users_status_page, user_games, user_games_page, user_activity, games_between, games_between_page, games_by_team, games_by_team_page, game, games_by_ids, games_by_ids_page, tournaments, tournament, tournament_standings, tournament_standings_page, tv_channels
