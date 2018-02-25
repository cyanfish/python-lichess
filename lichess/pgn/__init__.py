from datetime import datetime
from six import StringIO

def _node(g, spec):
    parts = spec.split('.')
    for p in parts:
        if p not in g:
            return None
        g = g[p]
    return str(g)

def _cap(s):
    if len(s) == 0:
        return s
    return s[0].upper() + s[1:]

def from_game(game, headers=None):
    if headers is None:
        headers = {}
    else:
        headers = dict(headers)
    g = game
    if 'moves' not in g:
        raise ValueError('The provided game doesn\'t have any moves. Maybe you forgot to set with_moves=1 on the API call?')

    result = '1/2-1/2' if _node(g, 'status') == 'draw' else '1-0' if _node(g, 'winner') == 'white' else '0-1' if _node(g, 'winner') == 'black' else '*'
    h = []
    h.append(("Event", "%s %s game" % ("Rated" if g["rated"] else "Casual", g["speed"])))
    h.append(('Site', g['url']))
    h.append(('Date', datetime.fromtimestamp(int(g['createdAt']) / 1000.0).strftime('%Y.%m.%d')))
    h.append(('Round', '?'))
    h.append(('White', _node(g, 'players.white.userId') or '?'))
    h.append(('Black', _node(g, 'players.black.userId') or '?'))
    h.append(('Result', result))
    h.append(('WhiteElo', _node(g, 'players.white.rating') or '?'))
    h.append(('BlackElo', _node(g, 'players.black.rating') or '?'))
    h.append(('ECO', _node(g, 'opening.eco')))
    h.append(('Opening', _node(g, 'opening.name')))
    if g['variant'] == 'fromPosition':
        h.append(('FEN', g['initialFen']))
    elif g['variant'] != 'standard':
        h.append(('Variant', _cap(g['variant'])))
    h.append(('TimeControl', _node(g, 'clock.initial') + '+' + _node(g, 'clock.increment')))
    moves = g['moves']
    pgn = ''
    for i in h:
        key = i[0]
        value = headers.pop(key, i[1])
        if value is not None:
            pgn += '[{} "{}"]\n'.format(key, value)
    pgn += '\n'
    ply = 0
    for m in moves.split(' '):
        if ply % 2 == 0:
            pgn += str(int(ply / 2 + 1)) + '. '
        pgn += m + ' '
        ply += 1
    pgn += result
    pgn += '\n'
    return pgn

def io_from_game(game, headers=None):
	return StringIO(from_game(game, headers))

def _validate_games(games):
    if isinstance(games, dict) and 'currentPageResults' in games:
        raise ValueError('The games argument must be a list. You provided a paginator. Use [\'currentPageResults\'] to get the games list, or prefix your API call with enumerate_ to abstract away paging.')

def from_games(games, headers=None):
    _validate_games(games)    
    return '\n'.join((from_game(g, headers) for g in games))

def save_games(games, path):
    _validate_games(games)
    with open(path, 'wb') as fout:
        first = True
        for g in games:
            if first:
                first = False
            else:
                fout.write('\n'.encode('utf-8'))
            fout.write(from_game(g).encode('utf-8'))
