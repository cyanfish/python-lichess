import lichess.api
import lichess.pgn
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
        online_count = len([u for u in users if u['online']])
        self.assertEqual(type(online_count), int)
    
    def test_user_activity(self):
        activity = lichess.api.user_activity('thibault')
        self.assertEqual(type(activity), list)
    
    def test_game(self):
        game = lichess.api.game('Qa7FJNk2', with_moves=1)
        self.assertEqual(type(game['moves']), str)
    
    def test_games_by_ids(self):
        games = lichess.api.games_by_ids(['Qa7FJNk2', '4M973EVR'], with_moves=1)
        lst = list(games)
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), str)
        self.assertEqual(type(moves2), str)
        self.assertNotEqual(moves1, moves2)

    def test_user_games(self):
        games = lichess.api.user_games('thibault', with_moves=1, nb=10)
        lst = list(itertools.islice(games, 2))
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), str)
        self.assertEqual(type(moves2), str)
        self.assertNotEqual(moves1, moves2)
    
    def test_games_between(self):
        games = lichess.api.games_between('atrophied', 'cyanfish', with_moves=1, nb=10)
        lst = list(itertools.islice(games, 2))
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), str)
        self.assertEqual(type(moves2), str)
        self.assertNotEqual(moves1, moves2)

    def test_games_by_team(self):
        games = lichess.api.games_by_team('programfox-senseifox-fanclub', with_moves=1, nb=10)
        lst = list(itertools.islice(games, 2))
        moves1 = lst[0]['moves']
        moves2 = lst[1]['moves']
        self.assertEqual(type(moves1), str)
        self.assertEqual(type(moves2), str)
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

class PgnIntegrationTestCase(unittest.TestCase):

    def test_pychess(self):
        api_game = lichess.api.game('Qa7FJNk2', with_moves=1)
        game = chess.pgn.read_game(lichess.pgn.io_from_game(api_game))
        fen = game.end().board().fen()
        self.assertEqual(fen, '2k1Rbr1/1ppr1Np1/p6p/8/3p4/P2P3P/1PP2PP1/2KR4 b - - 2 19')

if __name__ == '__main__':
    unittest.main()
