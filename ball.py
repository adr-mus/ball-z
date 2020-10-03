import math, os.path

import pygame

from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Ball(pygame.sprite.Sprite):
    image = pygame.image.load(os.path.join("images", "ball.png"))

    MAXSPEED = 12

    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 3 * SCREEN_HEIGHT // 4))

        self.vx = 4
        self.vy = -3

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

    def update_v(self, alpha):
        v_mag = math.sqrt(self.vx ** 2 + self.vy ** 2)
        v_mag = min(self.MAXSPEED, v_mag + 0.5)

        self.vx = round(v_mag * math.cos(alpha))
        self.vy = -round(v_mag * max(math.sin(alpha), 0.2))

    def hit(self, tile):
        if not self.is_bullet:  # FIXME: correct collistion detection
            x1, y1 = tile.rect.center
            x2, y2 = self.rect.center
            dx, dy = x2 - x1, y2 - y1
            if -0.5 * dx <= dy <= 0.5 * dx or 0.5 * dx <= dy <= -0.5 * dx:
                self.vx = -self.vx
            else:
                self.vy = -self.vy

        tile.on_hit()

