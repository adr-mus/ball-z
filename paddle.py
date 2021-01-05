""" Module containing the Paddle class. """

import math
import os

import pygame

from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Paddle(pygame.sprite.Sprite):
    """ Class representing the paddle. """
    images = {"base": pygame.image.load(os.path.join("images", "paddle.png")),
              "magnetic": pygame.image.load(os.path.join("images", "magnetic_paddle.png"))}

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.len = 0 # between -2 and 2
        self.image = self.images["base"]
        self.rect = self.image.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)
        )
        self.attached_balls = set()

        # bonuses
        self.is_magnetic = False
        self.is_confused = False

    def __len__(self):
        return self.rect.width

    def update(self, *, dx=None, paused=False):
        """ Updates the postion of the paddle.

            Parameters
                dx: int - position difference (used in testing)
                paused: bool - whether the game is paused """
        if dx is None:
            dx, _ = pygame.mouse.get_rel()
        if paused:
            return
            
        if self.is_confused:
            dx *= -1
        left, right = self.rect.left, self.rect.right
        self.rect.move_ip(dx, 0)

        # stop at boundary
        if self.rect.left <= MARGIN:
            self.rect.left = MARGIN
            dx = MARGIN - left
        elif self.rect.right >= SCREEN_WIDTH - MARGIN:
            self.rect.right = SCREEN_WIDTH - MARGIN
            dx = SCREEN_WIDTH - MARGIN - right

        for ball in self.attached_balls:
            ball.rect.move_ip(dx, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def resize(self, length):
        """ Changes the length of the paddle.
            Parameters
                - length: int from -2 to 2  """
        self.len = length
        w, h = self.images["base"].get_size()
        self.image = pygame.transform.scale(
            self.image, (int(w * 2 ** self.len), h)
        )
        self.rect = self.image.get_rect(center=self.rect.center)