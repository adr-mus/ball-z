# pylint: disable=no-member,missing-module-docstring,missing-class-docstring,missing-function-docstring,invalid-name

import unittest
import math

import pygame

import events
from game import Game
from ball import Ball
from bonuses import * # pylint: disable=wildcard-import,unused-wildcard-import


pygame.init()
pygame.mixer.set_num_channels(0)

game = Game.RunningGame()


class BonusTestCase(unittest.TestCase):
    def test_on_collect(self):
        Bonus.on_collect()
        self.assertEqual(pygame.event.poll().type, events.POINTS)
        self.assertEqual(pygame.event.poll().type, events.BONUS_COLLECTED)

    def test_random_bonus(self):
        random_bonus(0, 0)
        self.assertEqual(pygame.event.poll().type, events.BONUS_DROPPED)


class DeathTestCase(unittest.TestCase):
    def test_take_effect(self):
        lives = game.lives
        Death.take_effect(game)
        self.assertEqual(game.lives, lives - 1)


class LifeTestCase(unittest.TestCase):
    def test_take_effect(self):
        lives = game.lives
        Life.take_effect(game)
        self.assertEqual(game.lives, lives + 1)


class SpeedUpTestCase(unittest.TestCase):
    def test_take_effect(self):
        SpeedUp.take_effect(game)
        for ball in game.lvl.balls:
            self.assertAlmostEqual(math.hypot(ball.vx, ball.vy), ball.MAXSPEED, -1)


class FireBallTestCase(unittest.TestCase):
    def test_take_effect(self):
        FireBall.take_effect(game)
        self.assertTrue(Ball.is_fiery)


class SplitTestCase(unittest.TestCase):
    def test_take_effect(self):
        n = len(game.lvl.balls)
        Split.take_effect(game)
        self.assertEqual(len(game.lvl.balls), 2 * n)


class MagnetTestCase(unittest.TestCase):
    def test_take_effect(self):
        Magnet.take_effect(game)
        self.assertTrue(game.lvl.paddle.is_magnetic)


class EnlargeTestCase(unittest.TestCase):
    def test_take_effect(self):
        ln = game.lvl.paddle.len
        Enlarge.take_effect(game)
        self.assertEqual(game.lvl.paddle.len, ln + 1)
        Enlarge.take_effect(game)
        Enlarge.take_effect(game)
        Enlarge.take_effect(game)
        self.assertEqual(game.lvl.paddle.len, 2)


class ShrinkTestCase(unittest.TestCase):
    def test_take_effect(self):
        ln = game.lvl.paddle.len
        Shrink.take_effect(game)
        self.assertEqual(game.lvl.paddle.len, ln - 1)
        Shrink.take_effect(game)
        Shrink.take_effect(game)
        Shrink.take_effect(game)
        Shrink.take_effect(game)
        Shrink.take_effect(game)
        self.assertEqual(game.lvl.paddle.len, -2)


class ConfuseTestCase(unittest.TestCase):
    def test_take_effect(self):
        Confuse.take_effect(game)
        self.assertTrue(game.lvl.paddle.is_confused)


if __name__ == "__main__":
    unittest.main()
    