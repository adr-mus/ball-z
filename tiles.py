# pylint: disable=missing-function-docstring
""" Module containing all tile types. """

import abc
import os
import random

import pygame

import events
from bonuses import random_bonus


class Tile(abc.ABC, pygame.sprite.Sprite):
    """ Base Tile class. Each subclass must be decorated with the register_type
        method in order for the Level class to know the mapping between in-file
        names of tiles and their corresponding classes. """
    p_bonus = 0.1 # probability of a bonus being dropped
    image = None  # to be specified in subclasses

    types = {} # the mapping between tile aliases and their corresponding classes

    @staticmethod
    def register_type(alias):
        """ Used to dynamically create the mapping between in-file tile names
            and their corresponding classes (Tile subclasses). """
        def wrapper(subcls):
            Tile.types[alias] = subcls
            return subcls

        return wrapper

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(left=x, top=y)

    @abc.abstractmethod
    def on_hit(self):
        """ Defines what happens when a particular tile is hit. """

    def kill(self):
        # base point value
        pygame.event.post(pygame.event.Event(events.POINTS, points=5))

        # roll a bonus
        if random.random() < self.p_bonus:
            random_bonus(*self.rect.center)

        # kill the tile
        pygame.sprite.Sprite.kill(self)


@Tile.register_type("r")
class RegularTile(Tile):
    """ Basic tile. Takes one hit to destroy. """
    image = pygame.image.load(os.path.join("images", "tiles", "regular.png"))
    sound = pygame.mixer.Sound(os.path.join("sounds", "r_death.wav"))

    sound.set_volume(0.4)

    def on_hit(self):
        self.sound.play()
        self.kill()


@Tile.register_type("g")
class GlassTile(Tile):
    """ Invisible tile that becomes visible after the first hit. After another hit
        the tile gets destroyed but the ball doesn't change its direction. """
    images = {"base": pygame.image.load(os.path.join("images", "tiles", "glass.png")),
              "hit": pygame.image.load(os.path.join("images", "tiles", "broken.png"))}
    sounds = {"hit": pygame.mixer.Sound(os.path.join("sounds", "g_hit.wav")),
              "death": pygame.mixer.Sound(os.path.join("sounds", "g_death.wav"))}

    sounds["hit"].set_volume(0.1)
    sounds["death"].set_volume(0.1)

    def __init__(self, x, y):
        self.image = self.images["base"]
        self.hit = False
        Tile.__init__(self, x, y)

    def on_hit(self):
        if not self.hit:
            self.sounds["hit"].play()
            pygame.event.post(pygame.event.Event(events.POINTS, points=5))
            self.image = self.images["hit"]
            self.hit = True
        else:
            self.sounds["death"].play()
            self.kill()


@Tile.register_type("b")
class Brick(Tile):
    """ Tile that basic ball can't destroy. """
    image = pygame.image.load(os.path.join("images", "tiles", "brick.png"))
    sound = pygame.mixer.Sound(os.path.join("sounds", "wall_hit.wav"))

    sound.set_volume(0.25)

    def on_hit(self):
        self.sound.play()


@Tile.register_type("u")
class UnstableTile(Tile):
    """ After a hit becomes explosive. """
    images = {"base": pygame.image.load(os.path.join("images", "tiles", "unstable.png")),
              "hit": pygame.image.load(os.path.join("images", "tiles", "explosive.png"))}
    sound = pygame.mixer.Sound(os.path.join("sounds", "u_hit.wav"))

    def __init__(self, x, y):
        self.hit = False
        self.image = self.images["base"]
        Tile.__init__(self, x, y)

    def on_hit(self):
        if not self.hit:
            pygame.event.post(pygame.event.Event(events.POINTS, points=5))
            self.sound.play()
            self.hit = True
            self.image = self.images["hit"]
        else:
            self.kill()

    def kill(self):
        pygame.event.post(pygame.event.Event(events.POINTS, points=10))
        pygame.event.post(pygame.event.Event(events.EXPLOSION, where=self.rect.topleft))
        Tile.kill(self)


@Tile.register_type("e")
class ExplosiveTile(Tile):
    """ Explodes when hit. """
    image = pygame.image.load(os.path.join("images", "tiles", "explosive.png"))

    def on_hit(self):
        self.kill()

    def kill(self):
        pygame.event.post(pygame.event.Event(events.POINTS, points=10))
        pygame.event.post(pygame.event.Event(events.EXPLOSION, where=self.rect.topleft))
        Tile.kill(self)
        