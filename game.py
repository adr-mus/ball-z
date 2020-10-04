import time, os.path, sys, math

import pygame

import events
from ball import Ball
from paddle import Paddle
from tiles import Tile
from bonuses import Bonus
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


pygame.font.init()


class Game:
    def __init__(self):
        self.state = Game.StartScreen()

    def draw(self, surface):
        self.state.draw(surface)

    def update(self):
        self.state.update()

    def eventloop(self):
        self.state.eventloop(self)

    class StartScreen:
        def __init__(self):
            self.timer = None

        def update(self):
            pass

        def draw(self, surface):
            if self.timer is None:
                self.timer = pygame.time.get_ticks()

            surface.fill(pygame.Color("black"))

            dt = pygame.time.get_ticks() - self.timer
            c = 150 + int(100 * math.sin(dt / 500))

            text = pygame.font.Font("chalk.ttf", 256).render(
                "BALL-Z", True, pygame.Color("white")
            )
            x = SCREEN_WIDTH // 2 - text.get_width() // 2
            y = (SCREEN_HEIGHT // 2 - text.get_height() // 2) // 2
            surface.blit(text, (x, y))

            if dt > 3000:
                text = pygame.font.Font("chalk.ttf", 42).render(
                    "Left Click to Start", True, (c, c, c)
                )
                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                y = 3 * SCREEN_HEIGHT // 4
                surface.blit(text, (x, y))

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    game.state = Game.RunningGame()

    class RunningGame:
        margin = pygame.image.load(os.path.join("images", "margin.png"))

        def __init__(self):
            self.n_lvl = 2
            self.lvl = Level(self.n_lvl)
            self.lvl_finished = False
            self.lives = 2
            self.score = 0
            self.paused = False

        def update(self):
            if not (self.lvl_finished or self.paused):
                self.lvl.update()
                if not self.lvl.balls:
                    self.on_death()
                elif not self.lvl.tiles:
                    self.lvl_finished = True
                else:
                    self.lvl.detect_collisions()

        def draw(self, surface):
            # background
            surface.fill(pygame.Color("black"))

            # margins
            surface.blit(self.margin, (10, 0))
            surface.blit(self.margin, (SCREEN_WIDTH - MARGIN, 0))

            # lives
            if self.lives > 0:
                text = pygame.font.Font("chalk.ttf", 60).render(
                    "I" * self.lives, True, pygame.Color("white")
                )
                surface.blit(text, (SCREEN_WIDTH - MARGIN - 10 - text.get_width(), 1))

            # score
            text = pygame.font.Font("chalk.ttf", 48).render(
                str(self.score), True, pygame.Color("white")
            )
            surface.blit(text, (MARGIN + 10, 1))

            # balls, tiles, paddle, bonuses
            self.lvl.draw(surface)

            # optional text
            if self.lvl_finished:
                text = pygame.font.Font("chalk.ttf", 72).render(
                    "Level Cleared!", True, pygame.Color("white")
                )
                w, h = text.get_size()
                surface.blit(
                    text,
                    ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2),
                )

            if self.paused:
                text = pygame.font.Font("chalk.ttf", 72).render(
                    "Pause", True, pygame.Color("white")
                )
                w, h = text.get_size()
                surface.blit(
                    text,
                    ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2),
                )

        def on_death(self):
            self.lives -= 1
            if self.lives < 0:
                self.on_defeat()
            else:
                self.lvl.on_death()

        def on_defeat(self):  # TO BE UPDATED
            self.lives += 1
            self.lvl.on_death()

        def next_level(self):
            self.n_lvl += 1
            try:
                self.lvl = Level(self.n_lvl)
            except FileNotFoundError:
                pygame.event.post(pygame.event.Event(events.VICTORY))
            else:
                self.lvl_finished = False

        def eventloop(self, game):
            for event in pygame.event.get():
                # if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                #     game.state = Game.Welcome()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p:
                        if self.paused:
                            self.paused = not self.paused
                        else:
                            self.paused = True
                elif event.type == events.BONUS_DROPPED:
                    self.lvl.bonuses.add(event.bonus)
                elif event.type == events.BONUS_COLLECTED:
                    event.bonus.take_effect(self)
                elif event.type == events.POINTS:
                    self.score += event.points
                elif self.lvl_finished and event.type == pygame.MOUSEBUTTONUP:
                    self.next_level()
                elif event.type == events.DEFEAT or event.type == events.VICTORY:
                    final_score = self.score + (self.n_lvl - 1) * 1000
                    game.state = Game.Ranking(final_score)

    class Ranking:
        pass


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
            tiles.add(
                Tile.types[alias](MARGIN + 60 * int(x), MARGIN + 30 * int(y), *args)
            )
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
            ball.on_hit(self.paddle)

        # paddle vs. bonuses
        for bonus in pygame.sprite.spritecollide(
            self.paddle, self.bonuses, dokill=True
        ):
            bonus.on_collect()

        # balls vs. tiles
        for ball in self.balls:
            for tile in pygame.sprite.spritecollide(ball, self.tiles, dokill=False):
                ball.hit(tile)
                break

    def on_death(self):
        time.sleep(1)

        self.paddle = Paddle()

        Ball.is_bullet = False
        self.balls.empty()
        self.balls.add(Ball())
