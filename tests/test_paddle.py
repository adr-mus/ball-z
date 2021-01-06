# pylint: disable=no-member,missing-module-docstring,missing-class-docstring,missing-function-docstring,invalid-name
import unittest

import pygame

from ball import Ball
from paddle import Paddle
from main import SCREEN_HEIGHT, SCREEN_WIDTH, MARGIN


pygame.init()
pygame.mixer.set_num_channels(0)


class PaddleTestCase(unittest.TestCase):
    def setUp(self):
        self.paddle = Paddle()
        self.paddle.rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN

    def test_init(self):
        msg = "invalid paddle length"
        self.assertIn(self.paddle.len, range(-2, 4), msg=msg)

        msg = "paddle shouldn't start with balls attached"
        self.assertFalse(self.paddle.attached_balls, msg=msg)

        msg = "paddle shoudn't start with bonuses"
        self.assertFalse(self.paddle.is_confused, msg=msg)
        self.assertFalse(self.paddle.is_magnetic, msg=msg)

    def test_len(self):
        msg = "wrong paddle length"
        self.assertEqual(len(self.paddle), self.paddle.rect.width, msg=msg)

    def test_update(self):
        ball = Ball()
        ball.rect.center = self.paddle.rect.center
        self.paddle.attached_balls.add(ball)
        x1, x2 = self.paddle.rect.left, ball.rect.left
        dx = 10
        self.paddle.update(dx=dx)

        msg = "wrong position after moving the paddle"
        self.assertEqual(self.paddle.rect.left, x1 + dx, msg=msg)

        msg = "attached ball didn't move along the paddle"
        self.assertEqual(ball.rect.left, x2 + dx, msg=msg)

        self.paddle.is_confused = True
        x0 = self.paddle.rect.left
        self.paddle.update(dx=dx)
        msg = "directions should be reversed"
        self.assertEqual(self.paddle.rect.left, x0 - dx, msg=msg)

        self.paddle.is_confused = False
        self.paddle.update(dx=SCREEN_WIDTH)

        msg = "paddle should stop moving at margins"
        self.assertEqual(self.paddle.rect.right, SCREEN_WIDTH - MARGIN, msg=msg)
        self.paddle.update(dx=-SCREEN_WIDTH)
        self.assertEqual(self.paddle.rect.left, MARGIN, msg=msg)

    def test_draw(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # pylint: disable=too-many-function-args
        self.paddle.draw(surface)
        msg = "paddle is not displayed"
        white = (255, 255, 255, 255)
        self.assertEqual(surface.get_at(self.paddle.rect.center), white, msg=msg)


if __name__ == "__main__":
    unittest.main()
