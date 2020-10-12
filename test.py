import lichess.api
import lichess.pgn
import lichess.format
import chess.pgn
import itertools
import unittest

class ApiIntegrationTestCase(unittest.TestCase):

    def test_user(self):
        user = lichess.api.user('thibault')
        rating = user['perfs']['blitz']['rating']
        self.assertEqual(type(rating), int)

    def test_users_by_team(self):
        users = lichess.api.users_by_team('coders', nb=10)
        lst = list(itertools.islice(users, 2))
        self.assertEqual(type(lst[0]['id']), str)
        self.assertEqual(len(lst), 2)

    def test_users_by_ids(self):
        users = lichess.api.users_by_ids(['thibault', 'cyanfish'])
        lst = list(users)
        rating1 = lst[0]['perfs']['blitz']['rating']
        rating2 = lst[1]['perfs']['blitz']['rating']
        self.assertEqual(type(rating1), int)
        self.assertEqual(type(rating2), int)
        self.assertNotEqual(rating1, rating2)

    def test_users_status(self):
        users = lichess.api.users_status(['thibault', 'cyanfish'])
        online_count = len([u for u in users if u.get('online')])
        self.assertEqual(type(online_count), int)

    def test_user_activity(self):
        activity = lichess.api.user_activity('thibault')
        self.assertEqual(type(activity), list)

    def test_game(self):
        game = lichess.api.game('Qa7FJNk2')
        self.assertEqual(type(game['moves']), type(u''))

    def test_game_pgn(self):
        pgn = lichess.api.game('Qa7FJNk2', format=lichess.format.PGN)
        self.assertEqual(pgn[:7], '[Event ')

    def test_game_pychess(self):
        game = lichess.api.game('Qa7FJNk2', format=lichess.format.PYCHESS)
        self.assertTrue('Event' in game.headers)

    def test_games_by_ids(self):
        games = lichess.api.games_by_ids(['Qa7FJNk2', '4M973EVR'], with_moves=1)
        lst = list(games)
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), type(u''))
        self.assertEqual(type(moves2), type(u''))
        self.assertNotEqual(moves1, moves2)

    def test_user_games(self):
        games = lichess.api.user_games('thibault', max=5)
        lst = list(itertools.islice(games, 2))
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), type(u''))
        self.assertEqual(type(moves2), type(u''))
        self.assertNotEqual(moves1, moves2)

    def test_user_games_pgn(self):
        pgns = lichess.api.user_games('thibault', max=5, format=lichess.format.PGN)
        lst = list(itertools.islice(pgns, 2))
        self.assertEqual(lst[0][:7], '[Event ')
        self.assertEqual(lst[1][:7], '[Event ')
        self.assertNotEqual(lst[0], lst[1])

    def test_user_games_single_pgn(self):
        pgn = lichess.api.user_games('thibault', max=5, format=lichess.format.SINGLE_PGN)
        lst = list(itertools.islice(pgn, 2))
        self.assertEqual(pgn[:7], '[Event ')

    def test_user_games_pychess(self):
        games = lichess.api.user_games('thibault', max=5, format=lichess.format.PYCHESS)
        lst = list(itertools.islice(games, 2))
        self.assertTrue('Event' in lst[0].headers)
        self.assertTrue('Event' in lst[1].headers)
        self.assertNotEqual(lst[0], lst[1])

    def test_games_by_team(self):
        games = lichess.api.games_by_team('programfox-senseifox-fanclub', with_moves=1, nb=10)
        lst = list(itertools.islice(games, 2))
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), type(u''))
        self.assertEqual(type(moves2), type(u''))
        self.assertNotEqual(moves1, moves2)

    def test_tournaments(self):
        tourns = lichess.api.tournaments()
        self.assertGreater(len(tourns), 0)

    def test_tournament(self):
        tourn = lichess.api.tournament('winter17')
        self.assertEqual(tourn['id'], 'winter17')

    def test_tournament_standings(self):
        stands = lichess.api.tournament_standings('winter17')
        first_20 = list(itertools.islice(stands, 20))
        self.assertEqual(first_20[0]['name'].lower(), 'lance5500')
        self.assertEqual(first_20[-1]['name'].lower(), 'mr_strange')

    def test_tv_channels(self):
        channels = lichess.api.tv_channels()
        self.assertEqual(type(channels['Blitz']), dict)

    def test_cloud_eval(self):
        evaluation = lichess.api.cloud_evaluation(fen="rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2", multiPv=5, variant="standard")
        pvs = evaluation['pvs']
        self.assertEqual(evaluation['fen'], "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")
        self.assertEqual(len(pvs), 5)

class PgnIntegrationTestCase(unittest.TestCase):

    def test_pychess(self):
        api_game = lichess.api.game('Qa7FJNk2')
        game = chess.pgn.read_game(lichess.pgn.io_from_game(api_game))
        fen = game.end().board().fen()
        self.assertEqual(fen, '2k1Rbr1/1ppr1Np1/p6p/8/3p4/P2P3P/1PP2PP1/2KR4 b - - 2 19')

if __name__ == '__main__':
    unittest.main()
