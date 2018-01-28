import json
import requests
import time
from six.moves import urllib


class ApiError(Exception):
    """The default class for API exceptions."""

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
        """Make an API call.

        Makes an HTTP request using `lichess.api.base_url`.
        Consecutive calls use a 1s delay.
        If HTTP 429 is received, retries indefinitely after a 1min delay.
        To intercept 429s (e.g. for debugging) set `lichess.api.on_rate_limit`. This won't affect the 1min delay (unless you raise).
        """
        if self._first_call:
            self._first_call = False
        else:
            time.sleep(1)
        
        while True:
            url = urllib.parse.urljoin(base_url, path)
            if post_data:
                resp = requests.post(url, params=params, data=post_data)
            else:
                resp = requests.get(url, params)
            if resp.status_code == 429:
                on_rate_limit(url)
                time.sleep(60)
            else:
                break
        
        if resp.status_code != 200:
            raise ApiError(resp.status_code, url, resp.text)
        
        return resp.json()


# Configurable defaults
default_client = DefaultApiClient()
base_url = 'https://lichess.org/'
on_rate_limit = lambda url: None


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

def user(username, client=None):
    return _api_get('/api/user/{}'.format(username), None, client)

def users_by_team(team, client=None, **kwargs):
    kwargs['team'] = team
    return _api_get('/api/user', kwargs, client)

def enumerate_users_by_team(*args, **kwargs):
    return _enum(users_by_team, args, kwargs)

def users_by_ids(ids, client=None):
    return _api_post('/api/users', None, ','.join(ids), client)

def enumerate_users_by_ids(*args, **kwargs):
    return _batch(users_by_ids, args, kwargs, 300)

def users_status(ids, client=None):
    return _api_get('/api/users/status', { 'ids': ','.join(ids) }, client)

def enumerate_users_status(*args, **kwargs):
    return _batch(users_status, args, kwargs, 40)

def user_games(username, client=None, **kwargs):
    return _api_get('/api/user/{}/games'.format(username), kwargs, client)

def enumerate_user_games(*args, **kwargs):
    return _enum(user_games, args, kwargs)

def user_activity(username, client=None):
    return _api_get('/api/user/{}/activity'.format(username), None, client)

def games_between(username1, username2, client=None, **kwargs):
    return _api_get('/api/games/vs/{}/{}'.format(username1, username2), kwargs, client)

def enumerate_games_between(*args, **kwargs):
    return _enum(games_between, args, kwargs)

def games_by_team(team, client=None, **kwargs):
    return _api_get('/api/games/team/{}'.format(team), kwargs, client)

def enumerate_games_by_team(*args, **kwargs):
    return _enum(games_by_team, args, kwargs)

def game(game_id, client=None, **kwargs):
    return _api_get('/api/game/{}'.format(game_id), kwargs, client)

def games_by_ids(ids, client=None, **kwargs):
    return _api_post('/api/games', kwargs, ','.join(ids), client)

def enumerate_games_by_ids(*args, **kwargs):
    return _batch(games_by_ids, args, kwargs, 300)

def tournaments(client=None, **kwargs):
    return _api_get('/api/tournament', kwargs, client)

def tournament(tournament_id, client=None, **kwargs):
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs, client)

def tournament_standings(tournament_id, client=None, **kwargs):
    return _api_get('/api/tournament/{}'.format(tournament_id), kwargs, client)['standing']

def enumerate_tournament_standings(*args, **kwargs):
    kwargs['page'] = 1
    while True:
        pag = tournament_standings(*args, **kwargs)
        for obj in pag['players']:
            yield obj
        if len(pag['players']) == 0:
            break
        kwargs['page'] += 1

def tv_channels(client=None, **kwargs):
    return _api_get('/tv/channels', kwargs, client)
