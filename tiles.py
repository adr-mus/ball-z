import abc, os.path, random

import pygame

import events
from bonuses import Bonus


class Tile(pygame.sprite.Sprite, abc.ABC):
    p_bonus = 1 # probability of a bonus being dropped
    image = None  # to be specified in subclasses

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

    @abc.abstractmethod
    def on_hit(self):
        pass

    def soften(self):  # makes the tile killable by one hit
        pass

    def kill(self):
        # roll a bonus
        if random.random() < self.p_bonus:
            Bonus.random_bonus(*self.rect.center)

        # kill the tile
        pygame.sprite.Sprite.kill(self)


@Tile.register_type("r")
class RegularTile(Tile):
    images = {
        color: pygame.image.load(os.path.join("images", "tiles", f"reg_{color}.png"))
        for color in ["red", "green", "blue", "yellow"]
    }
    sounds = {"on_hit": pygame.mixer.Sound(os.path.join("sounds", "tiles", "r_death.wav"))}

    sounds["on_hit"].set_volume(0.4)

    def __init__(self, x, y, color="green"):
        self.image = self.images[color]
        Tile.__init__(self, x, y)
    
    def on_hit(self):
        self.sounds["on_hit"].play()
        pygame.event.post(pygame.event.Event(events.POINTS, points=5))
        self.kill()


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
        pygame.event.post(pygame.event.Event(events.POINTS, points=5))
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

@Tile.register_type("e")
class ExplosiveTile(Tile):
    image = pygame.image.load(os.path.join("images", "tiles", "reg_red.png"))

    def on_hit(self):
        pygame.event.post(pygame.event.Event(events.POINTS, points=15))
        self.kill()
    
    def kill(self):
        pygame.event.post(pygame.event.Event(events.EXPLOSION, where=self.rect.topleft))
        Tile.kill(self)