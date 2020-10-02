import time, os.path

import pygame

from ball import Ball
from paddle import Paddle
from tiles import Tile
from bonuses import Bonus


class clr:
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


life_image = pygame.image.load(os.path.join("images", "life.png"))


class Level:
    game = None
    def __init__(self, i):
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())
        self.bonuses = pygame.sprite.Group()

        tiles = pygame.sprite.Group()
        for line in open(os.path.join("levels", f"{i}.txt")):
            alias, x, y, *args = line.split()
            if alias not in Tile.tile_types:
                raise ValueError("invalid tile type")
            tiles.add(Tile.tile_types[alias](20 + 30 * int(x), 27 + 15 * int(y), *args))
        self.tiles = tiles
    
    def draw(self, surface):
        surface.fill(clr.BLACK)

        pygame.draw.line(surface, clr.WHITE, (19, 0), (19, 479))
        pygame.draw.line(surface, clr.WHITE, (621, 0), (621, 479))

        for i in range(self.game.lives):
            surface.blit(life_image, (604 - i*16, 1))

        self.paddle.draw(surface)
        self.balls.draw(surface)
        self.tiles.draw(surface)
        self.bonuses.draw(surface)


    def update(self):
        self.paddle.update()
        self.balls.update()
        self.bonuses.update()
    
    def detect_collisions(self):
        # paddle vs. balls
        for ball in pygame.sprite.spritecollide(self.paddle, self.balls, False):
            self.paddle.hit(ball)
        
        # paddle vs. bonuses
        for bonus in pygame.sprite.spritecollide(self.paddle, self.bonuses, True):
            bonus.on_collect()

        # balls vs. tiles
        for ball in self.balls:
            for tile in pygame.sprite.spritecollide(ball, self.tiles, False):
                if Game.collided_tile(ball, tile):
                    ball.hit(tile)
                    tile.on_hit()
                    break

    def on_death(self):
        time.sleep(1)
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())


class Game:
    def __init__(self):
        Level.game = self
        Bonus.game = self
        self.level = 1
        self.lvl = Level(self.level)
        self.lives = 2
        self.score = 0

    @staticmethod
    def collided_tile(ball, tile):
        x, y = ball.rect.center
        return (
            y + 4 >= tile.rect.top
            or y - 4 <= tile.rect.bottom
            or x + 4 >= tile.rect.left
            or x - 4 <= tile.rect.right
        )
    
    def update(self, surface):
        self.lvl.update()
        self.lvl.draw(surface)

        if not self.lvl.balls:
            self.on_death()
            return

        self.lvl.detect_collisions()
    
    def on_death(self):
        self.lives -= 1
        if self.lives < 0:
            self.on_defeat()
        else:
            self.lvl.on_death()
    
    def on_defeat(self): # TO BE UPDATED
        self.lives += 1
        self.lvl.on_death()



