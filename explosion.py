# pylint: disable=missing-function-docstring,invalid-name
""" Module defining the Explosion class. """

import os

import pygame


class Explosion(pygame.sprite.Sprite):
    """ Class representing a visual/acustic explosion. """
    images = [
        pygame.image.load(os.path.join("images", "explosion", f"{i}.png")) for i in range(1, 7)
    ]
    sound = pygame.mixer.Sound(os.path.join("sounds", "explode.wav"))

    sound.set_volume(0.1)

    def __init__(self, x, y, mute=False):
        pygame.sprite.Sprite.__init__(self)

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.timer = pygame.time.get_ticks()
        if not mute:
            self.sound.play()

    def update(self):
        """ Animation of the explosion. """
        dt = pygame.time.get_ticks() - self.timer
        i = int(6 * dt // 250)
        if i < len(self.images):
            self.image = self.images[i]
        else:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
