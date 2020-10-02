import enum, abc, os.path

import pygame
from pygame.locals import *

from bonuses import Bonus


class Tile(pygame.sprite.Sprite, abc.ABC):
    # used to dynamically create a dict of form alias: a Tile subclass
    # aliases are used to build levels from txt files
    tile_types = {}
    @staticmethod
    def register_tile(alias):
        def wrapper(subcls):
            Tile.tile_types[alias] = subcls
            return subcls

        return wrapper

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.surf = pygame.Surface((30, 15))
        self.rect = self.surf.get_rect(left=x, top=y)

    def on_hit(self):
        self.kill()
    
    def soften(self): # makes the tile killable by one hit
        pass

    def kill(self):
        # roll a bonus
        Bonus.random_bonus(*self.rect.center)
        
        # kill the tile
        pygame.sprite.Sprite.kill(self)


@Tile.register_tile("r")
class RegularTile(Tile):
    def __init__(self, x, y, color="red"):
        Tile.__init__(self, x, y)
        self.image = pygame.image.load(os.path.join("images", "tiles", f"reg_{color}.png"))


@Tile.register_tile("g")
class GlassTile(Tile):
    image_hit = pygame.image.load(os.path.join("images", "tiles", "glass_broken.png"))
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = pygame.image.load(os.path.join("images", "tiles", "glass.png"))
        self.hit = False
    
    def on_hit(self):
        if not self.hit:
            self.image = self.image_hit
            self.hit = True
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