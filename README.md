# python-lichess
Python client for the lichess.org API.

`lichess.api` contains thin wrappers for [API methods](https://github.com/ornicar/lila#http-api).

```
import lichess.api

user = lichess.api.user('cyanfish')
# {'id': 'cyanfish', 'username': 'cyanfish', ...

games = lichess.api.user_games('cyanfish', nb=20, with_moves=1)
# {'currentPage': 1, 'maxPerPage': 20, 'currentPageResults': [{"id":"ALwDtvYL", ...
```

For API methods that use paging, `enumerate_*` variations are provided that abstract the paging away.

```
import itertools

games = lichess.api.enumerate_user_games('cyanfish', nb=100, with_moves=1)
# Generator for lazily reading games from pages

games = itertools.islice(games, 500)
# 500 games, lazily read from 5 pages
```

`lichess.pgn` contains functions to generate PGNs from games.

```
import lichess.pgn

lichess.pgn.save_games(games, 'my_games.pgn')
```
