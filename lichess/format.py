from six import StringIO
import re
import json

GAME_STREAM_OBJECT = 'game_stream'
STREAM_OBJECT = 'stream'
PUBLIC_API_OBJECT = 'public_api'
MOBILE_API_OBJECT = 'mobile_api'


class _FormatBase(object):

    def content_type(self, object_type):
        return None
    
    def stream(self, object_type):
        return False
    
    def parse(self, object_type, resp):
        pass


class _Pgn(_FormatBase):

    def content_type(self, object_type):
        if object_type != GAME_STREAM_OBJECT:
            raise ValueError('PGN format is only valid for games')
        return 'application/x-chess-pgn'
    
    def parse(self, object_type, resp):
        return [pgn + '\n' for pgn in resp.text.split('\n\n\n')]


PGN = _Pgn()


class _PyChess(_FormatBase):

    def content_type(self, object_type):
        if object_type != GAME_STREAM_OBJECT:
            raise ValueError('PyChess format is only valid for games')
        return 'application/x-chess-pgn'
    
    def parse(self, object_type, resp):
        try:
            import chess.pgn
        except ImportError:
            raise ImportError('PyChess format requires the python-chess package to be installed')
        return [chess.pgn.read_game(StringIO(pgn)) for pgn in resp.text.split('\n\n\n')]


PYCHESS = _PyChess()


class _Json(_FormatBase):

    def content_type(self, object_type):
        if object_type == STREAM_OBJECT or object_type == GAME_STREAM_OBJECT:
            return 'application/x-ndjson'
        if object_type == MOBILE_API_OBJECT:
            return 'application/vnd.lichess.v3+json'
        return None
    
    def stream(self, object_type):
        return object_type == STREAM_OBJECT or object_type == GAME_STREAM_OBJECT

    def parse(self, object_type, resp):
        if object_type == STREAM_OBJECT or object_type == GAME_STREAM_OBJECT:
            return (json.loads(s) for s in resp.iter_lines())
        return json.loads(resp.text)


JSON = _Json()


class _Cookies(_FormatBase):

    def content_type(self, object_type):
        return 'application/vnd.lichess.v3+json'

    def parse(self, object_type, resp):
        return resp.cookies


COOKIES = _Cookies()
