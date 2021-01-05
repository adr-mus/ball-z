""" Module contatining the Ball class. """

import math
import os

import pygame

import events
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


pygame.mixer.init(buffer=128)


class Ball(pygame.sprite.Sprite):
    images = {"base": pygame.image.load(os.path.join("images", "ball.png")),
              "fiery": pygame.image.load(os.path.join("images", "fiery_ball.png"))}
    image = images["base"] # the current image shared between all balls
    sounds = {"paddle_hit": pygame.mixer.Sound(os.path.join("sounds", "paddle.ogg")),
              "wall_hit": pygame.mixer.Sound(os.path.join("sounds", "wall_hit.wav"))}
        
    # sound adjustments
    sounds["paddle_hit"].set_volume(0.05)
    sounds["wall_hit"].set_volume(0.25)

    MAXSPEED = 20

    # collected bonuses
    is_tiny = False
    is_fiery = False

    @classmethod
    def reset_state(cls):
        cls.is_tiny = False
        cls.is_fiery = False
        cls.image = cls.images["base"]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - MARGIN - 20))

        # initial speed components
        self.vx = self.MAXSPEED // 3
        self.vy = self.MAXSPEED // 3

        self.is_attached = True # attached to the paddle?

    def update(self):
        """ Moves the ball and changes its direction if a boundary has
            been hit or kills it if it has disappeared from the screen. """
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
            elif self.rect.top > SCREEN_HEIGHT + MARGIN:
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def on_hit(self, paddle):
        """ Triggered when the ball hits the paddle. """
        if not self.is_attached and paddle.is_magnetic:
            self.rect.bottom = paddle.rect.top - 1
            self.is_attached = True
            paddle.attached_balls.add(self)
        else:
            self.sounds["paddle_hit"].play()

            if not self.is_attached:
                self.rect.move_ip(-self.vx, -self.vy)
            self.is_attached = False

            paddle_x = paddle.rect.center[0]
            ball_x = self.rect.center[0]

            # change the direction of the ball
            min_alpha = math.pi / 12
            alpha = -math.pi * (ball_x - paddle_x) / len(paddle) + math.pi / 2
            if abs(alpha - math.pi / 2) < min_alpha:
                alpha = math.pi / 2 + math.copysign(min_alpha, alpha - math.pi / 2)
            elif abs(alpha - math.pi / 2) > math.pi / 2 - min_alpha:
                alpha = math.pi / 2 + math.copysign(math.pi / 2 - min_alpha, alpha - math.pi / 2)
            self.rect.bottom = paddle.rect.top - 1

            v_mag = math.hypot(self.vx, self.vy)
            v_mag = min(self.MAXSPEED, v_mag + 0.33) # increment the magnitude of the speed vector

            self.vx = round(v_mag * math.cos(alpha))
            self.vy = -round(v_mag * math.sin(alpha))

    def hit(self, tile):
        """ Triggered when the ball hits a tile. """
        from tiles import GlassTile

        # change the direction of the ball    
        self.rect.move_ip(-self.vx, -self.vy)    
        if not (isinstance(tile, GlassTile) and tile.hit):
            x1, y1 = tile.rect.center
            x2, y2 = self.rect.center
            dx, dy = x2 - x1, y2 - y1
            if  -dx <= 1.8 * dy <= dx or dx <= 1.8 * dy <= -dx:
                self.vx *= -1
            else:
                self.vy *= -1
        
        if self.is_fiery:
            tile.kill()
            pygame.event.post(pygame.event.Event(events.EXPLOSION, where=tile.rect.topleft))
        else:
            tile.on_hit()
