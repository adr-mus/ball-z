import unittest
import math

import pygame

import events
from ball import Ball
from paddle import Paddle
from tiles import RegularTile
from main import SCREEN_HEIGHT, SCREEN_WIDTH, MARGIN


class BallTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.mixer.set_num_channels(0)

    def setUp(self):
        self.ball = Ball()
        self.ball.rect.center = (SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2)
        self.ball.vx, self.ball.vy = 1, 1
    
    def test_reset_state(self):
        Ball.is_fiery = True
        Ball.is_tiny = True
        Ball.image = None
        Ball.reset_state()

        msg = "state hasn't been reset properly"
        self.assertFalse(Ball.is_fiery, msg=msg)
        self.assertFalse(Ball.is_tiny, msg=msg)
        self.assertEqual(Ball.image, Ball.images["base"], msg=msg)

    def test_init(self):
        msg = "ball shouldn't start with bonuses"
        self.assertFalse(self.ball.is_fiery, msg=msg)
        self.assertFalse(self.ball.is_tiny, msg=msg)

        msg = "ball should start attached"
        self.assertTrue(self.ball.is_attached, msg=msg)

    def test_update(self):
        x0, y0 = self.ball.rect.center
        self.ball.update()

        msg = "attached ball shouldn't move by itself"
        self.assertEqual((x0, y0), self.ball.rect.center, msg=msg)

        self.ball.is_attached = False
        self.ball.update()

        msg = "wrong position update"
        self.assertEqual((x0 + self.ball.vx, y0 + self.ball.vy), self.ball.rect.center, msg=msg)

        self.ball.rect.center = MARGIN, SCREEN_HEIGHT // 2
        vx, vy = -1, -1
        self.ball.vx, self.ball.vy = vx, vy
        self.ball.update()

        msg = "wrong position after hitting the left margin"
        self.assertGreaterEqual(self.ball.rect.left, MARGIN, msg=msg)

        msg = "wrong speed after hitting the left margin"
        self.assertAlmostEqual(self.ball.vx, -vx, msg=msg)
        self.assertAlmostEqual(self.ball.vy, vy, msg=msg)

        self.ball.rect.center = SCREEN_WIDTH - MARGIN, SCREEN_HEIGHT // 2
        vx, vy = 1, -1
        self.ball.vx, self.ball.vy = vx, vy
        self.ball.update()

        msg = "wrong position after hitting the right margin"
        self.assertLessEqual(self.ball.rect.right, SCREEN_WIDTH - MARGIN, msg=msg)

        msg = "wrong speed after hitting the right margin"
        self.assertAlmostEqual(self.ball.vx, -vx, msg=msg)
        self.assertAlmostEqual(self.ball.vy, vy, msg=msg)

        self.ball.rect.center = SCREEN_WIDTH // 2, 2 * MARGIN
        vx, vy = -1, -1
        self.ball.vx, self.ball.vy = vx, vy
        self.ball.update()

        msg = "wrong position after hitting the top"
        self.assertGreaterEqual(self.ball.rect.top, 2 * MARGIN, msg=msg)

        msg = "wrong speed after hitting the top"
        self.assertAlmostEqual(self.ball.vx, vx, msg=msg)
        self.assertAlmostEqual(self.ball.vy, -vy, msg=msg)

        self.ball.rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT + 2 * MARGIN
        ball_group = pygame.sprite.Group()
        ball_group.add(self.ball)

        msg = "ball added to a group but not present there (PYGAME ISSUE)"
        self.assertTrue(self.ball.alive(), msg=msg)
        self.ball.update()

        msg = "ball disappeared but is not dead"
        self.assertFalse(self.ball.alive(), msg=msg)
    
    def test_draw(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.ball.draw(surface)

        msg = "ball is not displayed"
        white = (255, 255, 255, 255)
        self.assertEqual(surface.get_at(self.ball.rect.center), white, msg=msg)

    def test_on_hit(self):
        paddle = Paddle()
        paddle.rect.center = self.ball.rect.left + 5, self.ball.rect.bottom + 1
        paddle.is_magnetic = True
        self.ball.is_attached = False
        vx, vy = self.ball.vx, self.ball.vy
        self.ball.on_hit(paddle)

        msg = "ball hit a magnetic paddle but didn't get attached"
        self.assertTrue(self.ball.is_attached, msg=msg)
        self.assertIn(self.ball, paddle.attached_balls, msg=msg)

        self.ball.on_hit(paddle)

        msg = "ball didn't get detached from the paddle"
        self.assertFalse(self.ball.is_attached, msg=msg)

        msg = "wrong ball direction after hitting the paddle"
        self.assertTrue(self.ball.vy * vy < 0, msg=msg)

        msg = "ball speed didn't increase after hitting the paddle"
        self.assertGreater(math.hypot(self.ball.vx, self.ball.vy), math.hypot(vx, vy), msg=msg)

        self.ball.rect.center = paddle.rect.left + 5, paddle.rect.top + 1
        self.ball.vx, self.ball.vy = self.ball.MAXSPEED * 3 // 5, self.ball.MAXSPEED * 4 // 5
        self.ball.on_hit(paddle)

        msg = "max ball speed exceded"
        self.assertLessEqual(math.hypot(self.ball.vx, self.ball.vy), self.ball.MAXSPEED, msg=msg)

    def test_hit(self):
        tile = RegularTile(self.ball.rect.center[0] + 10, self.ball.rect.center[1] + 10)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        vx, vy = self.ball.vx, self.ball.vy
        self.ball.hit(tile)

        msg = "wrong ball direction after hit"
        self.assertAlmostEqual(self.ball.vx, vx, msg=msg)
        self.assertAlmostEqual(self.ball.vy, -vy, msg=msg)

        msg = "tile hit but not updated"
        self.assertFalse(tile.alive(), msg=msg)
        self.assertEqual(pygame.event.poll().type, events.POINTS, msg=msg)

        self.ball.is_fiery = True
        tile = RegularTile(self.ball.rect.center[0] + 10, self.ball.rect.center[1])
        vx, vy = self.ball.vx, self.ball.vy
        self.ball.hit(tile)

        msg = "wrong ball direction after hit"
        self.assertAlmostEqual(self.ball.vx, -vx, msg=msg)
        self.assertAlmostEqual(self.ball.vy, vy, msg=msg)

        msg = "ball is fiery but there was no explosion after hit"
        self.assertIn(events.EXPLOSION, (event.type for event in pygame.event.get()), msg=msg)
        

if __name__ == "__main__":
    unittest.main()