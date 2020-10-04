import math, os.path

import pygame

from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Ball(pygame.sprite.Sprite):
    image = pygame.image.load(os.path.join("images", "ball.png"))

    MAXSPEED = 18

    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        self.vx = 10
        self.vy = -4

        self.is_attached = False

    def update(self):
        if not self.is_attached:
            self.rect.move_ip(self.vx, self.vy)

            if self.rect.left <= MARGIN:
                self.rect.left = MARGIN
                self.vx *= -1
            elif self.rect.right >= SCREEN_WIDTH - MARGIN:
                self.rect.right = SCREEN_WIDTH - MARGIN
                self.vx *= -1
            elif self.rect.top <= MARGIN:
                self.rect.top = MARGIN
                self.vy *= -1

            if self.rect.top > SCREEN_HEIGHT + MARGIN:
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def on_hit(self, paddle):
        self.rect.move_ip(-self.vx, -self.vy)
        if self.rect.top > paddle.rect.top:
            self.vx *= -1
        else:
            paddle_x = paddle.rect.center[0]
            ball_x = self.rect.center[0]

            alpha = -math.pi * (ball_x - paddle_x) / len(paddle) + math.pi / 2
            self.rect.bottom = paddle.rect.top - 5

            v_mag = math.hypot(self.vx, self.vy)
            v_mag = min(self.MAXSPEED, v_mag + 0.5)

            self.vx = round(v_mag * math.cos(alpha))
            self.vy = -round(v_mag * max(math.sin(alpha), 0.2))

    def hit(self, tile):
        if not self.is_bullet:
            self.rect.move_ip(-self.vx, -self.vy)
            x1, y1 = tile.rect.center
            x2, y2 = self.rect.center
            dx, dy = x2 - x1, y2 - y1
            if -0.5 * dx <= dy <= 0.5 * dx or 0.5 * dx <= dy <= -0.5 * dx:
                self.vx *= -1
            else:
                self.vy *= -1

        tile.on_hit()
