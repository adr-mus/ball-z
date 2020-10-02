import math, os.path

import pygame


class Ball(pygame.sprite.Sprite):
    MAXSPEED = 12

    image = pygame.image.load(os.path.join("images", "ball.png"))
    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.surf = pygame.Surface((8, 8))
        self.rect = self.surf.get_rect(center=(40, 177))

        self.vx = 3
        self.vy = 1

        self.is_attached = False

    def update(self):
        if not self.is_attached:
            self.rect.move_ip(self.vx, self.vy)

            if self.rect.left <= 20:
                self.rect.left = 21
                self.vx = -self.vx
            elif self.rect.right >= 620:
                self.rect.right = 619
                self.vx = -self.vx
            elif self.rect.top <= 27:
                self.rect.top = 28
                self.vy = -self.vy

            if self.rect.top > 485:
                self.kill()
                # self.rect.top = 28

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_v(self, alpha, factor):
        v_mag = math.sqrt(self.vx ** 2 + self.vy ** 2)
        v_mag = min(self.MAXSPEED, v_mag * factor)

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


class Life(pygame.sprite.Sprite):
    image = pygame.image.load(r"images\life.png")
    def __init__(self, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(top=1, right=640 - 30*i)
