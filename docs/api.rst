API Methods
==========================================

These functions are thin wrappers around the `lichess API <https://github.com/ornicar/lila#http-api>`_.

Each function takes an optional :data:`client` argument. See :doc:`api-config` for more information.

.. automodule:: lichess.api
    :members: user, users_by_team, enumerate_users_by_team, users_by_ids, enumerate_users_by_ids, users_status, enumerate_users_status, user_games, enumerate_user_games, user_activity, games_between, enumerate_games_between, games_by_team, enumerate_games_by_team, game, games_by_ids, enumerate_games_by_ids, tournaments, tournament, tournament_standings, enumerate_tournament_standings, tv_channels
