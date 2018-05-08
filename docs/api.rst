API Methods
==========================================

The module :mod:`lichess.api` provides thin wrappers around the `lichess API <https://lichess.org/api>`_.

In addition to the API parameters, each function takes optional :mod:`format <lichess.format>`, :mod:`auth <lichess.auth>`, and :doc:`client <api-config>` arguments.

Endpoints that return collections (like :data:`~lichess.api.user_games`) stream the results by returning a generator.

.. automodule:: lichess.api
    :members: user, users_by_team, users_by_ids, users_status, user_games, user_activity, games_by_team, game, games_by_ids, tournaments, tournament, tournament_standings, tv_channels
