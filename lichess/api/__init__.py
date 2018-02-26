import json
import requests
import time
from six.moves import urllib


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
    
    def __init__(self):
        self._first_call = True
    
    def call(self, path, params=None, post_data=None):
        """Make an API call, prepending :data:`lichess.api.base_url` to the provided path.

        Consecutive calls use a 1s delay.
        If HTTP 429 is received, retries indefinitely after a 1min delay.
        To log or raise an exception on a 429, set :data:`lichess.api.on_rate_limit`.
        """
        if self._first_call:
            self._first_call = False
        else:
            time.sleep(1)
        
        retry_count = 0
        while True:
            url = urllib.parse.urljoin(base_url, path)
            if post_data:
                resp = requests.post(url, params=params, data=post_data)
            else:
                resp = requests.get(url, params)
            if resp.status_code == 429:
                on_rate_limit(url, retry_count)
                time.sleep(60)
                retry_count += 1
            else:
                break
        
        if resp.status_code != 200:
            raise ApiHttpError(resp.status_code, url, resp.text)
        
        return resp.json()


default_client = DefaultApiClient()
"""The client object used to communicate with the lichess API.

Initially set to an instance of :class:`~lichess.api.DefaultApiClient`, you can customize it to change rate-limiting or error-handling behavior.
"""

base_url = 'https://lichess.org/'
"""The base lichess API URL used by :class:`~lichess.api.DefaultApiClient`.

This does not include the /api/ prefix, since some APIs don't use it.
"""

on_rate_limit = lambda url, retry_count: None
"""A handler called by :class:`~lichess.api.DefaultApiClient` when HTTP 429 is received.

Set it to a new value to log rate-limiting events, or to raise an exception if you don't want indefinite retries.

>>> def on_rate_limit(url, retry_count):
>>>     if retry_count > 3:
>>>         raise lichess.api.ApiError('Exceeded max retries')
>>> lichess.api.on_rate_limit = on_rate_limit
"""


# Helpers for API functions

def _api_get(path, params, client):
    if not client:
        client = default_client
    return client.call(path, params)

def _api_post(path, params, post_data, client):
    if not client:
        client = default_client
    return client.call(path, params, post_data)

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

def user(username, client=None, **kwargs):
    """Wrapper for the `GET /api/user/<username> <https://github.com/ornicar/lila#get-apiuserusername-fetch-one-user>`_ endpoint.
    
    >>> user = lichess.api.user('thibault')
    >>> print(user.get('perfs', {}).get('blitz', {}).get('rating'))
    1617
    """
    return _api_get('/api/user/{}'.format(username), kwargs, client)

def users_by_team(team, client=None, **kwargs):
    """Wrapper for the `GET /api/user <https://github.com/ornicar/lila#get-apiuser-fetch-many-users-from-a-team>`_ endpoint."""
    kwargs['team'] = team
    return _api_get('/api/user', kwargs, client)

def enumerate_users_by_team(*args, **kwargs):
    """See :data:`~lichess.api.users_by_team`. Returns a generator that makes requests for additional pages as needed.

    >>> users = lichess.api.enumerate_users_by_team('coders')
    >>> ratings = [u.get('perfs', {}).get('blitz', {}).get('rating') for u in users]
    >>> print(ratings)
    [1349, 1609, ...]
    """
    return _enum(users_by_team, args, kwargs)

def users_by_ids(ids, client=None, **kwargs):
    """Wrapper for the `POST /api/users <https://github.com/ornicar/lila#post-apiusers-fetch-many-users-by-id>`_ endpoint."""
    return _api_post('/api/users', kwargs, ','.join(ids), client)

def enumerate_users_by_ids(*args, **kwargs):
    """See :data:`~lichess.api.users_by_ids`. Returns a generator that splits the IDs into multiple requests as needed.

    >>> users = lichess.api.enumerate_users_by_ids(['thibault', 'cyanfish'])
    >>> ratings = [u.get('perfs', {}).get('blitz', {}).get('rating') for u in users]
    >>> print(ratings)
    [1617, 1948]
    """
    return _batch(users_by_ids, args, kwargs, 300)

def users_status(ids, client=None, **kwargs):
    """Wrapper for the `GET /api/users/status <https://github.com/ornicar/lila#get-apiusersstatus-fetch-many-users-online-and-playing-flags>`_ endpoint."""
    kwargs['ids'] = ','.join(ids)
    return _api_get('/api/users/status', kwargs, client)

def enumerate_users_status(*args, **kwargs):
    """See :data:`~lichess.api.users_status`. Returns a generator that makes requests for additional pages as needed.

    >>> users = lichess.api.enumerate_users_by_ids(['thibault', 'cyanfish'])
    >>> online_count = len([u for u in users if u['online']])
    >>> print(online_count)
    1
    """
    return _batch(users_status, args, kwargs, 40)

def user_games(username, client=None, **kwargs):
    """Wrapper for the `GET /api/user/<username>/games <https://github.com/ornicar/lila#get-apiuserusernamegames-fetch-user-games>`_ endpoint."""
    return _api_get('/api/user/{}/games'.format(username), kwargs, client)

def enumerate_user_games(*args, **kwargs):
    """See :data:`~lichess.api.user_games`. Returns a generator that makes requests for additional pages as needed."""
    return _enum(user_games, args, kwargs)

def user_activity(username, client=None, **kwargs):
    """Wrapper for the `GET /api/user/<username>/activity <https://github.com/ornicar/lila#get-apiuserusernameactivity-fetch-recent-user-activity>`_ endpoint."""
    return _api_get('/api/user/{}/activity'.format(username), kwargs, client)

def games_between(username1, username2, client=None, **kwargs):
    """Wrapper for the `GET /api/games/vs/<username>/<username> <https://github.com/ornicar/lila#get-apigamesvsusernameusername-fetch-games-between-2-users>`_ endpoint."""
    return _api_get('/api/games/vs/{}/{}'.format(username1, username2), kwargs, client)

def enumerate_games_between(*args, **kwargs):
    """See :data:`~lichess.api.games_between`. Returns a generator that makes requests for additional pages as needed."""
    return _enum(games_between, args, kwargs)

def games_by_team(team, client=None, **kwargs):
    """Wrapper for the `GET /api/games/team/<teamId> <https://github.com/ornicar/lila#get-apigamesteamteamid-fetch-games-between-players-of-a-team>`_ endpoint."""
    return _api_get('/api/games/team/{}'.format(team), kwargs, client)

def enumerate_games_by_team(*args, **kwargs):
    """See :data:`~lichess.api.games_by_team`. Returns a generator that makes requests for additional pages as needed."""
    return _enum(games_by_team, args, kwargs)

def game(game_id, client=None, **kwargs):
    """Wrapper for the `GET /api/game/{id} <https://github.com/ornicar/lila#get-apigameid-fetch-one-game-by-id>`_ endpoint."""
    return _api_get('/api/game/{}'.format(game_id), kwargs, client)

def games_by_ids(ids, client=None, **kwargs):
    """Wrapper for the `POST /api/games <https://github.com/ornicar/lila#post-apigames-fetch-many-games-by-id>`_ endpoint."""
    return _api_post('/api/games', kwargs, ','.join(ids), client)

def enumerate_games_by_ids(*args, **kwargs):
    """See :data:`~lichess.api.games_by_ids`. Returns a generator that splits the IDs into multiple requests as needed."""
    return _batch(games_by_ids, args, kwargs, 300)

def tournaments(client=None, **kwargs):
    """Wrapper for the `GET /api/tournament <https://github.com/ornicar/lila#get-apitournament-fetch-current-tournaments>`_ endpoint."""
    return _api_get('/api/tournament', kwargs, client)

def tournament(tournament_id, client=None, **kwargs):
    """Wrapper for the `GET /api/tournament/<tournamentId> <https://github.com/ornicar/lila#get-apitournamenttournamentid-fetch-one-tournament>`_ endpoint."""
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs, client)

def tournament_standings(tournament_id, client=None, **kwargs):
    """Wrapper for the `GET /api/tournament/<tournamentId> <https://github.com/ornicar/lila#get-apitournamenttournamentid-fetch-one-tournament>`_ endpoint."""
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs, client)['standing']

def enumerate_tournament_standings(*args, **kwargs):
    """See :data:`~lichess.api.tournament_standings`. Returns a generator that makes requests for additional pages as needed."""
    kwargs['page'] = 1
    while True:
        pag = tournament_standings(*args, **kwargs)
        for obj in pag['players']:
            yield obj
        if len(pag['players']) == 0:
            break
        kwargs['page'] += 1

def tv_channels(client=None, **kwargs):
    """Wrapper for the `GET /tv/channels <https://github.com/ornicar/lila#get-tvchannels-fetch-current-tournaments>`_ endpoint."""
    return _api_get('/tv/channels', kwargs, client)
