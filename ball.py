import math, os.path

import pygame

import events
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN

pygame.mixer.init(buffer=128)


class Ball(pygame.sprite.Sprite):
    base_image = pygame.image.load(os.path.join("images", "ball.png"))
    image = base_image
    sounds = {"paddle_hit": pygame.mixer.Sound(os.path.join("sounds", "paddle.ogg")),
              "wall_hit": pygame.mixer.Sound(os.path.join("sounds", "wall_hit.wav"))}
        
    # sound adjustments
    sounds["paddle_hit"].set_volume(0.1)

    MAXSPEED = 24

    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - MARGIN - 20))

        self.vx = self.MAXSPEED // 4
        self.vy = self.MAXSPEED // 4

        self.is_attached = True

    def update(self):
        if not self.is_attached:
            self.rect.move_ip(self.vx, self.vy)

            if self.rect.left <= MARGIN:
                self.sounds["wall_hit"].play()
                self.rect.left = MARGIN
                self.vx *= -1
            elif self.rect.right >= SCREEN_WIDTH - MARGIN:
                self.sounds["wall_hit"].play()
                self.rect.right = SCREEN_WIDTH - MARGIN
                self.vx *= -1
            elif self.rect.top <= 2 * MARGIN:
                self.sounds["wall_hit"].play()
                self.rect.top = 2 * MARGIN
                self.vy *= -1

            if self.rect.top > SCREEN_HEIGHT + MARGIN:
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def on_hit(self, paddle):
        if not self.is_attached and paddle.is_magnetic:
            self.rect.bottom = paddle.rect.top - 1
            self.is_attached = True
            paddle.attached_balls.add(self)
        else:
            self.sounds["paddle_hit"].play()
            if not self.is_attached:
                self.rect.move_ip(-self.vx, -self.vy)
            self.is_attached = False
            if self.rect.top > paddle.rect.top:
                self.vx *= -1
            else:
                paddle_x = paddle.rect.center[0]
                ball_x = self.rect.center[0]

                alpha = -math.pi * (ball_x - paddle_x) / len(paddle) + math.pi / 2
                self.rect.bottom = paddle.rect.top - 5

                v_mag = math.hypot(self.vx, self.vy)
                v_mag = min(self.MAXSPEED, v_mag + 1)


                self.vx = round(v_mag * math.cos(alpha))
                self.vy = -round(v_mag * max(math.sin(alpha), 0.2))

    def hit(self, tile):
        self.rect.move_ip(-self.vx, -self.vy)
        x1, y1 = tile.rect.center
        x2, y2 = self.rect.center
        dx, dy = x2 - x1, y2 - y1
        if  -dx <= 2 * dy <= dx or dx <= 2 * dy <= -dx:
            self.vx *= -1
        else:
            self.vy *= -1
        
        if self.is_fiery:
            tile.kill()
            pygame.event.post(pygame.event.Event(events.EXPLOSION, where=tile.rect.topleft))
        else:
            tile.on_hit()
