import unittest
import math

import pygame

import events
from tiles import *


pygame.init()
pygame.mixer.set_num_channels(0)


class RegularTileTestCase(unittest.TestCase):
    def test_on_hit(self):
        tile = RegularTile(0, 0)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        tile.on_hit()
        self.assertFalse(tile.alive())


class GlassTileTestCase(unittest.TestCase):
    def test_on_hit(self):
        tile = GlassTile(0, 0)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        tile.on_hit()
        self.assertTrue(tile.alive())
        tile.on_hit()
        self.assertFalse(tile.alive())


class BrickTestCase(unittest.TestCase):
    def test_on_hit(self):
        tile = Brick(0, 0)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        for _ in range(10):
            tile.on_hit()
        self.assertTrue(tile.alive())


class UnstableTileTestCase(unittest.TestCase):
    def test_on_hit(self):
        tile = UnstableTile(0, 0)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        tile.on_hit()
        self.assertTrue(tile.alive())
        tile.on_hit()
        self.assertFalse(tile.alive())
        self.assertIn(events.EXPLOSION, (event.type for event in pygame.event.get()))


class ExplosiveTileTestCase(unittest.TestCase):
    def test_on_hit(self):
        tile = ExplosiveTile(0, 0)
        tile_group = pygame.sprite.Group()
        tile_group.add(tile)
        tile.on_hit()
        self.assertFalse(tile.alive())
        self.assertIn(events.EXPLOSION, (event.type for event in pygame.event.get()))


if __name__ == "__main__":
    unittest.main()
