# pylint: disable=invalid-name,missing-function-docstring
""" Module containing the Level class. """

import os
import time
import pickle

import pygame

import events
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN
from fonts import message_font
from ball import Ball
from paddle import Paddle
from tiles import Tile, Brick
from explosion import Explosion


class Level: # pylint: disable=too-many-instance-attributes
    """ Class representing a level. It keeps track of all sprites:
        balls, the paddle, tiles, explosions and bonuses. """
    sounds = {
        "death": pygame.mixer.Sound(os.path.join("sounds", "death.wav")),
        "next_level": pygame.mixer.Sound(os.path.join("sounds", "next_level.wav")),
    }

    def __init__(self, n):
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        ball = Ball()
        self.balls.add(ball)
        self.paddle.attached_balls.add(ball)

        self.tile_matrix = [[None for _ in range(16)] for _ in range(16)]
        self.tiles = pygame.sprite.Group()
        if n != 0:  # case n = 0 is used for testing
            with open(os.path.join("levels", f"{n}.pkl"), "rb") as file:
                file = pickle.load(file)
                for line in file.split("\n"):
                    try:
                        j, i, alias = line.split()
                        if alias not in Tile.types:
                            raise RuntimeError(f"invalid tile type: {alias}")
                        i, j = int(i), int(j)
                        tile = Tile.types[alias](MARGIN + 60 * i, 3 * MARGIN + 30 * j)
                        self.tile_matrix[i][j] = tile
                        self.tiles.add(tile)
                    except (TypeError, ValueError):
                        pass

        self.bonuses = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        self.n = n
        self.finished = False
        self.paused = False
        Ball.reset_state()

    def draw(self, surface):
        # draw all sprites
        self.explosions.draw(surface)
        self.paddle.draw(surface)
        self.balls.draw(surface)
        self.tiles.draw(surface)
        self.bonuses.draw(surface)

        # conditional text
        if self.finished:
            message = "Level Cleared!"
            text = message_font.render(message, True, pygame.Color("white"))
            w, h = text.get_size()
            x, y = (SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2
            surface.blit(text, (x, y))
        elif self.paused:
            text = message_font.render("Pause", True, pygame.Color("white"))
            w, h = text.get_size()
            x, y = (SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2
            surface.blit(text, (x, y))

    def update(self):
        """ Updates the postions of all sprites. """
        self.paddle.update(paused=self.finished or self.paused)
        if not (self.finished or self.paused):
            self.balls.update()
            self.bonuses.update()
            if not self.balls:
                pygame.event.post(pygame.event.Event(events.DEATH))
            elif all(isinstance(tile, Brick) for tile in self.tiles):
                self.finished = True
                self.sounds["next_level"].play()
            else:
                self.detect_collisions()
        self.explosions.update()

    def detect_collisions(self):
        """ Detects sprite collisions. """
        # paddle vs. balls
        for ball in pygame.sprite.spritecollide(self.paddle, self.balls, False):
            ball.on_hit(self.paddle)

        # paddle vs. bonuses
        for bonus in pygame.sprite.spritecollide(self.paddle, self.bonuses, True):
            bonus.on_collect()

        # balls vs. tiles
        for ball in self.balls:
            for tile in pygame.sprite.spritecollide(ball, self.tiles, False):
                ball.hit(tile)
                break

    def explosion(self, x, y):
        """ Trigerred when an explosion occurs. Destoys all tiles around
            the explosion center. """
        i, j = (x - MARGIN) // 60, (y - 3 * MARGIN) // 30
        for k in range(-1, 2):
            for l in range(-1, 2):
                try:
                    tile = self.tile_matrix[i + k][j + l]
                    x, y = MARGIN + 60 * (i + k) + 30, 3 * MARGIN + 30 * (j + l) + 15
                    if MARGIN < x <= SCREEN_WIDTH - MARGIN:
                        mute = not (k == 0 and l == 0)
                        self.explosions.add(Explosion(x, y, mute=mute))
                        if tile.alive():
                            tile.kill()
                except (AttributeError, IndexError):
                    pass

    def on_death(self):
        """ Triggered when player loses all balls. """
        if self.n != 0:
            self.sounds["death"].play()
            time.sleep(1)

        Ball.reset_state()

        # refresh paddle, ball, delete bonuses
        self.bonuses.empty()
        self.paddle = Paddle()
        self.balls.empty()
        ball = Ball()
        self.balls.add(ball)
        self.paddle.attached_balls.add(ball)
