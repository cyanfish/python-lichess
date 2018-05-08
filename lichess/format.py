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


class _SinglePgn(_Pgn):

    def parse(self, object_type, resp):
        return resp.text


SINGLE_PGN = _SinglePgn()


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


class _Cookies(_FormatBase):

    def content_type(self, object_type):
        return 'application/vnd.lichess.v3+json'

    def parse(self, object_type, resp):
        return resp.cookies


COOKIES = _Cookies()
