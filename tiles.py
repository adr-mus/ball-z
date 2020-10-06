import abc, os.path, random

import pygame

import events
from bonuses import Bonus


class Tile(pygame.sprite.Sprite, abc.ABC):
    p_bonus = 0.2 # probability of a bonus being dropped
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

    def kill(self):
        # base point value
        pygame.event.post(pygame.event.Event(events.POINTS, points=5))

        # roll a bonus
        if random.random() < self.p_bonus:
            Bonus.random_bonus(*self.rect.center)

        # kill the tile
        pygame.sprite.Sprite.kill(self)


@Tile.register_type("r")
class RegularTile(Tile):
    image = pygame.image.load(os.path.join("images", "tiles", "regular.png"))
    sound = pygame.mixer.Sound(os.path.join("sounds", "r_death.wav"))

    sound.set_volume(0.4)
    
    def on_hit(self):
        self.sound.play()
        self.kill()


@Tile.register_type("g")
class GlassTile(Tile):
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
    image = pygame.image.load(os.path.join("images", "tiles", "brick.png"))
    sound = pygame.mixer.Sound(os.path.join("sounds", "wall_hit.wav"))
    
    def on_hit(self):
        self.sound.play()


@Tile.register_type("u")
class UnstableTile(Tile):
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
    image = pygame.image.load(os.path.join("images", "tiles", "explosive.png"))

    def on_hit(self):
        self.kill()
    
    def kill(self):
        pygame.event.post(pygame.event.Event(events.POINTS, points=10))
        pygame.event.post(pygame.event.Event(events.EXPLOSION, where=self.rect.topleft))
        Tile.kill(self)
        