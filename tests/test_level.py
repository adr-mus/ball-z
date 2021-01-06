# pylint: disable=no-member,missing-module-docstring,missing-class-docstring,missing-function-docstring,invalid-name
import unittest

import pygame

import events
from main import MARGIN
from level import Level
from tiles import RegularTile
from bonuses import FireBall


class LevelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.mixer.set_num_channels(0)

    def setUp(self):
        self.lvl = Level(0)
        self.ball = self.lvl.balls.sprites()[0]
        tile = RegularTile(MARGIN, 3 * MARGIN)
        self.lvl.tile_matrix[0][0] = tile
        self.lvl.tiles.add(tile)

    def test_init(self):
        self.assertEqual(len(self.lvl.balls), 1)
        self.assertIn(self.ball, self.lvl.paddle.attached_balls)
        self.assertFalse(self.lvl.finished)
        self.assertFalse(self.lvl.paused)

    def test_update(self):
        self.lvl.tile_matrix[0][0].kill()
        self.lvl.update()
        self.assertTrue(self.lvl.finished)

        self.ball.kill()
        self.lvl.update()
        self.assertNotIn(events.DEATH, (event.type for event in pygame.event.get()))

        self.lvl.finished = False

        self.ball.kill()
        self.lvl.update()
        self.assertIn(events.DEATH, (event.type for event in pygame.event.get()))

    def test_detect_collisions(self):
        self.ball.rect.center = self.lvl.paddle.rect.center
        self.lvl.detect_collisions()
        self.assertLess(self.ball.vy, 0)

        self.ball.rect.center = self.lvl.tile_matrix[0][0].rect.center
        self.lvl.detect_collisions()
        self.assertFalse(self.lvl.tile_matrix[0][0].alive())

        bonus = FireBall(*self.lvl.paddle.rect.center)
        self.lvl.detect_collisions()
        self.assertFalse(bonus.alive())

    def test_explosion(self):
        self.lvl.explosion(60 + MARGIN, 30 + 3 * MARGIN)
        self.assertFalse(self.lvl.tile_matrix[0][0].alive())
        self.assertTrue(self.lvl.explosions)

    def test_on_death(self):
        paddle = self.lvl.paddle
        self.lvl.bonuses.add(FireBall(0, 0))
        self.lvl.on_death()
        self.assertIsNot(paddle, self.lvl.paddle)
        self.assertFalse(self.lvl.bonuses)
        self.assertIsNot(self.lvl.balls.sprites()[0], self.ball)


if __name__ == "__main__":
    unittest.main()
