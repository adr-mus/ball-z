import time, os.path, sys

import pygame

from ball import Ball
from paddle import Paddle
from tiles import Tile
from bonuses import Bonus


life_image = pygame.image.load(os.path.join("images", "life.png"))

pygame.font.init()


class Game:
    def __init__(self):
        self.state = Game.Welcome()

    def draw(self, surface):
        self.state.draw(surface)

    def update(self):
        self.state.update()

    def eventloop(self):
        self.state.eventloop(self)

    class Welcome:
        def __init__(self):
            self.drawn = False

        def update(self):
            pass

        def draw(self, surface):
            if not self.drawn:
                surface.fill(pygame.Color("black"))

                pygame.draw.aaline(surface, pygame.Color("white"), (19, 0), (19, 479), 3)
                pygame.draw.aaline(surface, pygame.Color("white"), (621, 0), (621, 479), 3)

                font = pygame.font.SysFont("CourierNew", 96, bold=True)
                score_text = font.render("BALL-Z", True, pygame.Color("white"))
                surface.blit(score_text, (145, 100))

                # mouse_left = pygame.image.load(os.path.join("images", "mouse_left.png"))
                # surface.blit(mouse_left, (50, 100))

                self.drawn = True

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    game.state = Game.RunningGame()

    class RunningGame:
        def __init__(self):
            self.level = 1
            self.lvl = Level(self.level)
            self.lives = 2
            self.score = 0

            Bonus.game = self

        def update(self):
            self.lvl.update()
            if not self.lvl.balls:
                self.on_death()
            elif not self.lvl.tiles:
                self.on_win()
            else:
                self.lvl.detect_collisions()

        def draw(self, surface):
            surface.fill(pygame.Color("black"))

            pygame.draw.aaline(surface, pygame.Color("white"), (19, 0), (19, 479), 3)
            pygame.draw.aaline(surface, pygame.Color("white"), (621, 0), (621, 479), 3)

            for i in range(self.lives):
                surface.blit(life_image, (604 - i * 16, 1))

            font = pygame.font.SysFont("CourierNew", 18, bold=True)
            score_text = font.render(str(self.score), True, pygame.Color("white"))
            surface.blit(score_text, (30, 1))

            self.lvl.draw(surface)

        def on_death(self):
            self.lives -= 1
            if self.lives < 0:
                self.on_defeat()
            else:
                self.lvl.on_death()

        def on_defeat(self):  # TO BE UPDATED
            self.lives += 1
            self.lvl.on_death()

        def on_win(self):
            pass

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    game.state = Game.Welcome()
                # elif event.type == pygame.MOUSEBUTTONUP:
                #     game.state = Game.RunningGame()


class Level:
    def __init__(self, i):
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())
        self.bonuses = pygame.sprite.Group()

        tiles = pygame.sprite.Group()
        for line in open(os.path.join("levels", f"{i}.txt")):
            alias, x, y, *args = line.split()
            if alias not in Tile.types:
                raise RuntimeError("invalid tile type")
            tiles.add(Tile.types[alias](20 + 30 * int(x), 27 + 15 * int(y), *args))
        self.tiles = tiles

    def draw(self, surface):
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
        for ball in pygame.sprite.spritecollide(self.paddle, self.balls, dokill=False):
            self.paddle.hit(ball)

        # paddle vs. bonuses
        for bonus in pygame.sprite.spritecollide(
            self.paddle, self.bonuses, dokill=True
        ):
            bonus.on_collect()

        # balls vs. tiles
        for ball in self.balls:
            for tile in pygame.sprite.spritecollide(ball, self.tiles, dokill=False):
                ball.hit(tile)

    def on_death(self):
        time.sleep(1)

        self.paddle = Paddle()

        Ball.is_bullet = False
        self.balls.empty()
        self.balls.add(Ball())
