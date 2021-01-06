# pylint: disable=no-member,missing-module-docstring,missing-class-docstring,missing-function-docstring,invalid-name
import unittest
import os
import pickle

import pygame

import events
from game import Game
from bonuses import FireBall


pygame.init()
pygame.mixer.set_num_channels(0)


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_init(self):
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))


class StartScreenTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(start_lvl=0)

    def test_eventloop(self):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP))
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.RunningGame))

        self.game.state = Game.StartScreen()

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_r)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.Ranking))

        self.game.state = Game.StartScreen()

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)
        pygame.event.post(event)
        with self.assertRaises(SystemExit):
            self.game.eventloop()


class RunningGameTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(start_lvl=0)
        self.game.state = Game.RunningGame(start_lvl=0)
        self.state = self.game.state

    def test_on_death(self):
        self.state.on_death()
        self.assertEqual(self.state.lives, 1)

        self.state.lives = 0
        self.state.on_death()
        self.assertIn(events.GAME_OVER, (event.type for event in pygame.event.get()))

    def test_next_level(self):
        self.state.n_lvl = -1
        self.state.next_level()
        self.assertEqual(self.state.n_lvl, 0)

        self.state.n_lvl = 100
        self.state.next_level()
        self.assertIn(events.GAME_OVER, (event.type for event in pygame.event.get()))

    def test_eventloop(self):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP))
        self.game.eventloop()
        self.assertFalse(self.state.lvl.paddle.attached_balls)

        self.state.n_lvl = -1
        self.state.lvl.finished = True
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP))
        self.game.eventloop()
        self.assertEqual(self.state.n_lvl, 0)

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_p)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(self.state.lvl.paused)

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_p)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertFalse(self.state.lvl.paused)

        bonus = FireBall(0, 0)

        event = pygame.event.Event(events.BONUS_DROPPED, bonus=bonus)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertIn(event.bonus, self.state.lvl.bonuses)

        event = pygame.event.Event(events.BONUS_COLLECTED, bonus=bonus)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(self.state.lvl.balls.sprites()[0].is_fiery)

        event = pygame.event.Event(events.POINTS, points=10)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertEqual(self.state.score, 10)

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))

        self.game.state = Game.RunningGame(start_lvl=0)
        event = pygame.event.Event(events.GAME_OVER, won=False)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.RankingTransition))


class RankingTransitionTestCase(unittest.TestCase):
    def setUp(self):
        Game.ranking_path = "test_rank.pkl"
        self.game = Game(start_lvl=0)
        self.game.state = Game.RankingTransition(score=-10, won=False)
        self.state = self.game.state

    def tearDown(self):
        try:
            os.remove(Game.ranking_path)
        except FileNotFoundError:
            pass

    def test_init(self):
        self.assertEqual(self.state.ranking, [])
        self.assertEqual(self.state.title, "Good Luck Next Time!")
        self.assertEqual(self.state.name, "")
        self.assertEqual(self.state.score, -10)
        self.assertTrue(self.state.ask_name)

    def test_update_ranking(self):
        self.state.name = "test"
        self.state.score = -1
        self.state.update_ranking()
        self.assertTrue(os.path.exists(Game.ranking_path))
        with open(Game.ranking_path, "rb") as f:
            rank = pickle.load(f)
        self.assertEqual(rank, [("test", -1)])

        test_rank = [("test", 5), ("test", 4), ("test", 3), ("test", 2), ("test", 1), ("test", 0)]
        self.state.ranking = list(reversed(test_rank))
        self.state.update_ranking()
        self.assertTrue(os.path.exists(Game.ranking_path))
        with open(Game.ranking_path, "rb") as f:
            rank = pickle.load(f)
        self.assertEqual(rank, self.state.ranking[-5:])

    def test_eventloop(self):
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_t, unicode="t")
        pygame.event.post(event)
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_e, unicode="e")
        pygame.event.post(event)
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_s, unicode="s")
        pygame.event.post(event)
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_t, unicode="t")
        pygame.event.post(event)
        self.game.eventloop()
        self.assertEqual(self.state.name, "test")

        self.state.name = "longtest"
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_t, unicode="t")
        pygame.event.post(event)
        self.game.eventloop()
        self.assertEqual(self.state.name, "longtest")

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_BACKSPACE)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertEqual(self.state.name, "longtes")

        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_RETURN)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.Ranking))

        self.game.state = Game.RankingTransition(score=-10, won=False)
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))


class RankingTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(start_lvl=0)
        self.game.state = Game.Ranking()

    def test_eventloop(self):
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))

        self.game.state = Game.Ranking()
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_r)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))

        self.game.state = Game.Ranking()
        event = pygame.event.Event(pygame.MOUSEBUTTONUP)
        pygame.event.post(event)
        self.game.eventloop()
        self.assertTrue(isinstance(self.game.state, Game.StartScreen))


if __name__ == "__main__":
    unittest.main()
    