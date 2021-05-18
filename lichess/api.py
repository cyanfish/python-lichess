import json
import requests
import time
from six.moves import urllib
import lichess.format
import lichess.auth


class ApiError(Exception):
    """The base class for API exceptions."""

class ApiHttpError(ApiError):
    """The class for API exceptions caused by an HTTP error code."""

    def __init__(self, http_status, url, response_text):
        self.http_status = http_status
        self.url = url
        self.response_text = response_text

    def __str__(self):
        return '{} {} {}'.format(self.http_status, self.url, self.response_text)

class DefaultApiClient(object):
    """
    The default API client, with immediate HTTP calls and basic rate-limiting functionality.
    """

    _first_call = True

    base_url = 'https://lichess.org/'
    """The base lichess API URL.

    This does not include the /api/ prefix, since some APIs don't use it.
    """

    max_retries = -1
    """The maximum number of retries after rate-limiting before an exception is raised. -1 for infinite retries."""

    def __init__(self, base_url=None, max_retries=None):
        if base_url is not None:
            self.base_url = base_url
        if max_retries is not None:
            self.max_retries = max_retries

    def call(self, path, params=None, post_data=None, auth=None, format=lichess.format.JSON, object_type=lichess.format.PUBLIC_API_OBJECT):
        """Makes an API call, prepending :data:`~lichess.api.DefaultApiClient.base_url` to the provided path. HTTP GET is used unless :data:`post_data` is provided.

        Consecutive calls use a 1s delay.
        If HTTP 429 is received, retries after a 1min delay.
        """
        if DefaultApiClient._first_call:
            DefaultApiClient._first_call = False
        else:
            time.sleep(1)

        if auth is None:
            auth = lichess.auth.EMPTY
        elif isinstance(auth, str):
            auth = lichess.auth.OAuthToken(auth)
        headers = auth.headers()
        stream = format.stream(object_type)
        content_type = format.content_type(object_type)
        if content_type:
            headers['Accept'] = content_type
        cookies = auth.cookies()

        retry_count = 0
        while True:
            url = urllib.parse.urljoin(self.base_url, path)
            if post_data:
                resp = requests.post(url, params=params, data=post_data, headers=headers, cookies=cookies, stream=stream)
            else:
                resp = requests.get(url, params, headers=headers, cookies=cookies, stream=stream)

            if resp.status_code == 429:
                self.on_rate_limit(url, retry_count)
                time.sleep(60)
                retry_count += 1
            elif resp.status_code == 502 or resp.status_code == 503:
                self.on_api_down(retry_count)
                time.sleep(60)
                retry_count += 1
            else:
                break

        if resp.status_code != 200:
            raise ApiHttpError(resp.status_code, url, resp.text)

        return format.parse(object_type, resp)

    def on_rate_limit(self, url, retry_count):
        """A handler called when HTTP 429 is received.

        Raises an exception when :data:`~lichess.api.DefaultApiClient.max_retries` is exceeded.
        """
        if self.max_retries != -1 and retry_count >= self.max_retries:
            raise ApiError('Max retries exceeded')

    def on_api_down(self, retry_count):
        """A handler called when HTTP 502 or HTTP 503 is received.

        Raises an exception when :data:`~lichess.api.DefaultApiClient.max_retries` is exceeded.
        """
        if self.max_retries != -1 and retry_count >= self.max_retries:
            raise ApiError('Max retries exceeded')

default_client = DefaultApiClient()
"""The client object used to communicate with the lichess API.

Initially set to an instance of :class:`~lichess.api.DefaultApiClient`.
"""


# Helpers for API functions

def _api_get(path, params, object_type=lichess.format.PUBLIC_API_OBJECT):
    client = params.pop('client', default_client)
    auth = params.pop('auth', lichess.auth.EMPTY)
    format = params.pop('format', lichess.format.JSON)
    return client.call(path, params, auth=auth, format=format, object_type=object_type)

def _api_post(path, params, post_data, object_type=lichess.format.PUBLIC_API_OBJECT):
    client = params.pop('client', default_client)
    auth = params.pop('auth', lichess.auth.EMPTY)
    format = params.pop('format', lichess.format.JSON)
    return client.call(path, params, post_data, auth=auth, format=format, object_type=object_type)

def _enum(fn, args, kwargs):
    if 'nb' not in kwargs:
        kwargs['nb'] = 100
    kwargs['page'] = 1
    while True:
        pag = fn(*args, **kwargs)
        if 'paginator' in pag:
            pag = pag['paginator']
        for obj in pag['currentPageResults']:
            yield obj
        if pag['nextPage'] is None or pag['currentPage'] != kwargs['page']:
            break
        kwargs['page'] += 1

def _batch(fn, args, kwargs, batch_size):
    if len(args) == 0:
        raise ValueError('A positional argument must be supplied')
    if not isinstance(args[0], list):
        raise ValueError('First argument must be a list')
    args = list(args)
    remaining = args[0]
    while len(remaining) > 0:
        args[0] = remaining[:batch_size]
        remaining = remaining[batch_size:]
        results = fn(*args, **kwargs)
        for obj in results:
            yield obj

# Actual public API functions

def user(username, **kwargs):
    """Wrapper for the `GET /api/user/<username> <https://github.com/ornicar/lila#get-apiuserusername-fetch-one-user>`_ endpoint.

    >>> user = lichess.api.user('thibault')
    >>> print(user.get('perfs', {}).get('blitz', {}).get('rating'))
    1617
    """
    return _api_get('/api/user/{}'.format(username), kwargs)

def users_by_team(team, **kwargs):
    """Wrapper for the `GET /api/team/{name}/users <https://github.com/ornicar/lila#get-apiuser-fetch-many-users-from-a-team>`_ endpoint.
    Returns a generator that streams the user data.

    >>> users = lichess.api.users_by_team('coders')
    >>> ratings = [u.get('perfs', {}).get('blitz', {}).get('rating') for u in users]
    >>> print(ratings)
    [1349, 1609, ...]
    """
    return _api_get('/api/team/{}/users'.format(team), kwargs, object_type=lichess.format.STREAM_OBJECT)

def users_by_ids(ids, **kwargs):
    """Wrapper for the `POST /api/users <https://github.com/ornicar/lila#post-apiusers-fetch-many-users-by-id>`_ endpoint.
    Returns a generator that splits the IDs into multiple requests as needed.

    Note: Use :data:`~lichess.api.users_status` when possible, since it is cheaper and not rate-limited.

    >>> users = lichess.api.users_by_ids(['thibault', 'cyanfish'])
    >>> ratings = [u.get('perfs', {}).get('blitz', {}).get('rating') for u in users]
    >>> print(ratings)
    [1617, 1948]
    """
    return _batch(users_by_ids_page, [ids], kwargs, 300)

def users_by_ids_page(ids, **kwargs):
    """Wrapper for the `POST /api/users <https://github.com/ornicar/lila#post-apiusers-fetch-many-users-by-id>`_ endpoint.
    Use :data:`~lichess.api.users_by_ids` to avoid manual pagination.
    """
    return _api_post('/api/users', kwargs, ','.join(ids))

def users_status(ids, **kwargs):
    """Wrapper for the `GET /api/users/status <https://github.com/ornicar/lila#get-apiusersstatus-fetch-many-users-online-and-playing-flags>`_ endpoint.
    Returns a generator that makes requests for additional pages as needed.

    Note: This endpoint is cheap and not rate-limited. Use it instead of :data:`~lichess.api.users_by_ids` when possible.

    >>> users = lichess.api.users_status(['thibault', 'cyanfish'])
    >>> online_count = len([u for u in users if u.get('online')])
    >>> print(online_count)
    1
    """
    return _batch(users_status_page, [ids], kwargs, 40)

def users_status_page(ids, **kwargs):
    """Wrapper for the `GET /api/users/status <https://github.com/ornicar/lila#get-apiusersstatus-fetch-many-users-online-and-playing-flags>`_ endpoint.
    Use :data:`~lichess.api.users_status` to avoid manual pagination.
    """
    kwargs['ids'] = ','.join(ids)
    return _api_get('/api/users/status', kwargs)

def user_activity(username, **kwargs):
    """Wrapper for the `GET /api/user/<username>/activity <https://github.com/ornicar/lila#get-apiuserusernameactivity-fetch-recent-user-activity>`_ endpoint."""
    return _api_get('/api/user/{}/activity'.format(username), kwargs)

def game(game_id, **kwargs):
    """Wrapper for the `GET /api/game/{id} <https://github.com/ornicar/lila#get-apigameid-fetch-one-game-by-id>`_ endpoint.

    By default, returns a dict representing a JSON game object.
    Use `format=PGN` for a PGN string or `format=PYCHESS` for a `python-chess <https://github.com/niklasf/python-chess>`_ game object.

    >>> game = lichess.api.game('Qa7FJNk2')
    >>> print(game['moves'])
    e4 e5 Nf3 Nc6 Bc4 Qf6 d3 h6 ...

    >>> from lichess.format import PGN, PYCHESS
    >>> pgn = lichess.api.game('Qa7FJNk2', format=PGN)
    >>> print(pgn)
    [Event "Casual rapid game"]
    ...

    >>> game_obj = lichess.api.game('Qa7FJNk2', format=PYCHESS)
    >>> print(game_obj.end().board())
    . . k . R b r .
    . p p r . N p .
    p . . . . . . p
    . . . . . . . .
    . . . p . . . .
    P . . P . . . P
    . P P . . P P .
    . . K R . . . .
    """
    return _api_get('/game/export/{}'.format(game_id), kwargs, object_type=lichess.format.GAME_OBJECT)

def games_by_ids(ids, **kwargs):
    """Wrapper for the `POST /games/export/_ids <https://github.com/ornicar/lila#post-apigames-fetch-many-games-by-id>`_ endpoint.
    Returns a generator that splits the IDs into multiple requests as needed."""
    return _batch(games_by_ids_page, [ids], kwargs, 300)

def games_by_ids_page(ids, **kwargs):
    """Wrapper for the `POST /games/export/_ids <https://github.com/ornicar/lila#post-apigames-fetch-many-games-by-id>`_ endpoint.
    Use :data:`~lichess.api.games_by_ids` to avoid manual pagination.
    """
    return _api_post('/games/export/_ids', kwargs, ','.join(ids), object_type=lichess.format.GAME_STREAM_OBJECT)

def user_games(username, **kwargs):
    """Wrapper for the `GET /api/user/<username>/games <https://github.com/ornicar/lila#get-apiuserusernamegames-fetch-user-games>`_ endpoint.

    By default, returns a generator that streams game objects.
    Use `format=PGN` for a generator of game PGNs, `format=SINGLE_PGN` for a single PGN string, or `format=PYCHESS` for a generator of `python-chess <https://github.com/niklasf/python-chess>`_ game objects.

    >>> games = lichess.api.user_games('cyanfish', max=50, perfType='blitz')
    >>> print(next(games)['moves'])
    e4 e5 Nf3 Nc6 Bc4 Qf6 d3 h6 ...

    >>> from lichess.format import PGN, SINGLE_PGN, PYCHESS
    >>> pgns = lichess.api.user_games('cyanfish', max=50, format=PGN)
    >>> print(next(pgns))
    [Event "Casual rapid game"]
    ...

    >>> pgn = lichess.api.user_games('cyanfish', max=50, format=SINGLE_PGN)
    >>> print(pgn)
    [Event "Casual rapid game"]
    ...

    >>> game_objs = lichess.api.user_games('cyanfish', max=50, format=PYCHESS)
    >>> print(next(game_objs).end().board())
    . . k . R b r .
    . p p r . N p .
    p . . . . . . p
    . . . . . . . .
    . . . p . . . .
    P . . P . . . P
    . P P . . P P .
    . . K R . . . .
    """
    return _api_get('/api/games/user/{}'.format(username), kwargs, object_type=lichess.format.GAME_STREAM_OBJECT)


def current_game(username, **kwargs):
    """Wrapper for the `GET /api/user/<username>/current-game` endpoint.
    Returns a single game."""
    return _api_get('/api/user/{}/current-game'.format(username), kwargs, object_type=lichess.format.GAME_OBJECT)

def tournaments(**kwargs):
    """Wrapper for the `GET /api/tournament <https://github.com/ornicar/lila#get-apitournament-fetch-current-tournaments>`_ endpoint."""
    return _api_get('/api/tournament', kwargs)

def tournament(tournament_id, **kwargs):
    """Wrapper for the `GET /api/tournament/<tournamentId> <https://github.com/ornicar/lila#get-apitournamenttournamentid-fetch-one-tournament>`_ endpoint."""
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs)

def tournament_standings(tournament_id, **kwargs):
    """Wrapper for the `GET /api/tournament/<tournamentId> <https://github.com/ornicar/lila#get-apitournamenttournamentid-fetch-one-tournament>`_ endpoint.
    Returns a generator that makes requests for additional pages as needed."""
    kwargs['page'] = 1
    while True:
        pag = tournament_standings_page(tournament_id, **kwargs)
        for obj in pag['players']:
            yield obj
        if len(pag['players']) == 0:
            break
        kwargs['page'] += 1

def tournament_standings_page(tournament_id, **kwargs):
    """Wrapper for the `GET /api/tournament/<tournamentId> <https://github.com/ornicar/lila#get-apitournamenttournamentid-fetch-one-tournament>`_ endpoint.
    Use :data:`~lichess.api.tournament_standings` to avoid manual pagination.
    """
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs)['standing']

def tv_channels(**kwargs):
    """Wrapper for the `GET /tv/channels <https://github.com/ornicar/lila#get-tvchannels-fetch-current-tournaments>`_ endpoint."""
    return _api_get('/tv/channels', kwargs)

def cloud_eval(fen, **kwargs):
    """Wrapper for the `GET api/cloud-eval <https://lichess.org/api#operation/apiCloudEval>`_ endpoint. """
    kwargs['fen'] = fen
    return _api_get('/api/cloud-eval', kwargs)

def login(username, password):
    cookie_jar = _api_post('/login', {'format': lichess.format.COOKIES}, {'username': username, 'password': password})
    return lichess.auth.Cookie(cookie_jar)
