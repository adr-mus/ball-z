import enum, abc, os.path

import pygame
from pygame.locals import *

from bonuses import Bonus


class Tile(pygame.sprite.Sprite, abc.ABC):
    image = None # to be specified in subclasses

    # used to dynamically create a dict of form alias: a Tile subclass
    # aliases are used to build levels from txt files
    types = {}
    @staticmethod
    def register_type(alias):
        def wrapper(subcls):
            Tile.types[alias] = subcls
            return subcls

        return wrapper

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(left=x, top=y)

    def on_hit(self):
        self.kill()
    
    def soften(self): # makes the tile killable by one hit
        pass

    def kill(self):
        # roll a bonus
        Bonus.random_bonus(*self.rect.center)
        
        # kill the tile
        pygame.sprite.Sprite.kill(self)


@Tile.register_type("r")
class RegularTile(Tile):
    images = {color: pygame.image.load(os.path.join("images", "tiles", f"reg_{color}.png"))
                for color in ["red", "green", "blue", "yellow"]}
    def __init__(self, x, y, color="green"):
        self.image = self.images[color]
        Tile.__init__(self, x, y)


@Tile.register_type("g")
class GlassTile(Tile):
    image_intact = pygame.image.load(os.path.join("images", "tiles", "glass.png"))
    image_hit = pygame.image.load(os.path.join("images", "tiles", "glass_broken.png"))
    def __init__(self, x, y):
        self.image = self.image_intact
        self.hit = False
        Tile.__init__(self, x, y)
    
    def soften(self):
        self.image = self.image_hit
        self.hit = True

    def on_hit(self):
        if not self.hit:
            self.soften()
        else:
            self.kill()



# class Brick(Tile):
#     def __init__(self):
#         self.hit = False
#         Tile.__init__(self)


# class TripleTile(Tile):
#     def __init__(self):
#         self.n_hits = 0
#         Tile.__init__(self)


class ExplosiveTile(Tile):
    def on_hit(self, ball):
        pass