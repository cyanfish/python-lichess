from six import StringIO
import re
import json

GAME_STREAM_OBJECT = 'game_stream'
STREAM_OBJECT = 'stream'
GAME_OBJECT = 'game'
PUBLIC_API_OBJECT = 'public_api'
MOBILE_API_OBJECT = 'mobile_api'


def stream_pgns(resp):
    buffer = []
    for line in resp.iter_lines():
        buffer.append(line.decode('utf-8'))
        if buffer[-2:] == ['', '']:
            yield '\n'.join(buffer)
            buffer.clear()
    if len(buffer) > 3:
        yield '\n'.join(buffer)


class _FormatBase(object):

    def content_type(self, object_type):
        return None
    
    def stream(self, object_type):
        return False
    
    def parse(self, object_type, resp):
        pass


class _Pgn(_FormatBase):

    def content_type(self, object_type):
        if object_type not in (GAME_STREAM_OBJECT, GAME_OBJECT):
            raise ValueError('PGN format is only valid for games')
        return 'application/x-chess-pgn'
    
    def stream(self, object_type):
        return object_type == GAME_STREAM_OBJECT

    def parse(self, object_type, resp):
        if object_type == GAME_STREAM_OBJECT:
            return stream_pgns(resp)
        return resp.text


PGN = _Pgn()
"""Produces a PGN string, or a generator for PGN strings of each game.

>>> from lichess.format import PGN
>>>
>>> pgn = lichess.api.game('Qa7FJNk2', format=PGN)
>>> print(pgn)
[Event "Casual rapid game"]
...
>>> pgns = lichess.api.user_games('cyanfish', max=50, format=PGN)
>>> print(len(list(pgns)))
50
"""


class _SinglePgn(_Pgn):

    def parse(self, object_type, resp):
        return resp.text


SINGLE_PGN = _SinglePgn()
"""Produces a PGN string, possibly containing multiple games.

>>> from lichess.format import0 SINGLE_PGN
>>>
>>> pgn = lichess.api.user_games('cyanfish', max=50, format=SINGLE_PGN)
>>> print(pgn)
[Event "Casual rapid game"]
...
"""


class _PyChess(_FormatBase):

    def content_type(self, object_type):
        if object_type not in (GAME_STREAM_OBJECT, GAME_OBJECT):
            raise ValueError('PyChess format is only valid for games')
        return 'application/x-chess-pgn'
    
    def parse(self, object_type, resp):
        try:
            import chess.pgn
        except ImportError:
            raise ImportError('PyChess format requires the python-chess package to be installed')
        if object_type == GAME_STREAM_OBJECT:
            return (chess.pgn.read_game(StringIO(pgn)) for pgn in stream_pgns(resp))
        return chess.pgn.read_game(StringIO(resp.text))


PYCHESS = _PyChess()
"""Produces a `python-chess <https://github.com/niklasf/python-chess>`_ game object, or a generator for multiple game objects.

>>> from lichess.format import PYCHESS
>>>
>>> game = lichess.api.game('Qa7FJNk2', format=PYCHESS)
>>> print(game.end().board())
. . k . R b r .
. p p r . N p .
p . . . . . . p
. . . . . . . .
. . . p . . . .
P . . P . . . P
. P P . . P P .
. . K R . . . .
"""


class _Json(_FormatBase):

    def content_type(self, object_type):
        if object_type in (STREAM_OBJECT, GAME_STREAM_OBJECT):
            return 'application/x-ndjson'
        if object_type == MOBILE_API_OBJECT:
            return 'application/vnd.lichess.v3+json'
        return 'application/json'
    
    def stream(self, object_type):
        return object_type in (STREAM_OBJECT, GAME_STREAM_OBJECT)

    def parse(self, object_type, resp):
        if object_type in (STREAM_OBJECT, GAME_STREAM_OBJECT):
            return (json.loads(s) for s in resp.iter_lines())
        return json.loads(resp.text)


JSON = _Json()
"""Produces a dict representing a JSON object, or a generator for multiple dicts. This is the default format.

>>> from lichess.format import JSON
>>>
>>> game = lichess.api.game('Qa7FJNk2', format=JSON) # or leave out
>>> print(game['players']['white']['user']['id'])
cyanfish
"""


class _Cookies(_FormatBase):

    def content_type(self, object_type):
        return 'application/vnd.lichess.v3+json'

    def parse(self, object_type, resp):
        return resp.cookies


COOKIES = _Cookies()
