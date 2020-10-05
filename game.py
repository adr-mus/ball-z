import time, os.path, sys, math

import pygame

import events
from ball import Ball
from paddle import Paddle
from tiles import Tile
from bonuses import Bonus
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN
from fonts import *


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
        music = pygame.mixer.Sound(os.path.join("sounds", "menu.wav"))

        def __init__(self):
            self.timer = None
            self.music.play()

        def update(self):
            pass

        def draw(self, surface):
            # timer for animations
            if self.timer is None:
                self.timer = pygame.time.get_ticks()
            dt = pygame.time.get_ticks() - self.timer

            # background
            surface.fill(pygame.Color("black"))

            # title
            c = min(int(255 * dt / 5000), 255)
            text = title_font.render("BALL-Z", True, (c, c, c))
            x = SCREEN_WIDTH // 2 - text.get_width() // 2
            y = (SCREEN_HEIGHT // 2 - text.get_height() // 2) // 2
            surface.blit(text, (x, y))

            # instruction
            if dt > 6000:
                c = 150 + int(100 * math.sin(dt / 500))
                text = message_font.render("Left Click to Start", True, (c, c, c))
                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                y = 3 * SCREEN_HEIGHT // 4
                surface.blit(text, (x, y))

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.music.fadeout(1000)
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
                # elif not self.lvl.tiles:
                #     self.lvl_finished = True
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
                lives = "I" * self.lives
                text = message_font.render(lives, True, pygame.Color("white"))
                surface.blit(text, (SCREEN_WIDTH - MARGIN - 10 - text.get_width(), 1))

            # score
            text = regular_font.render(str(self.score), True, pygame.Color("white"))
            surface.blit(text, (MARGIN + 10, 1))

            # balls, tiles, paddle, bonuses
            self.lvl.draw(surface)

            # conditional text
            if self.lvl_finished:
                message = "Level Cleared!"
                text = message_font.render(message, True, pygame.Color("white"))
                w, h = text.get_size()
                x, y = (SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2
                surface.blit(text, (x, y))
            if self.paused:
                text = message_font.render("Pause", True, pygame.Color("white"))
                w, h = text.get_size()
                x, y = (SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2
                surface.blit(text, (x, y))

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
                elif event.type == pygame.MOUSEBUTTONUP:
                    for ball in self.lvl.paddle.attached_balls:
                        ball.on_hit(self.lvl.paddle)
                    self.lvl.paddle.attached_balls.clear()
                elif event.type == events.EXPLOSION:
                    x, y = event.where
                    i, j = (x - MARGIN) // 60, (y - 3 * MARGIN) // 30
                    self.lvl.explosion(i, j)
                elif event.type == events.DEFEAT or event.type == events.VICTORY:
                    final_score = self.score + (self.n_lvl - 1) * 1000
                    game.state = Game.Ranking(final_score)

    class Ranking:
        pass
        # def update(self):
        #     pass

        # def draw(self, surface):
        #     if self.timer is None:
        #         self.timer = pygame.time.get_ticks()

        #     surface.fill(pygame.Color("black"))

        #     dt = pygame.time.get_ticks() - self.timer
        #     c = 150 + int(100 * math.sin(dt / 500))

        #     text = pygame.font.Font("chalk.ttf", 48).render(
        #         "Best Scores", True, pygame.Color("white")
        #     )
        #     x = SCREEN_WIDTH // 2 - text.get_width() // 2
        #     y = (SCREEN_HEIGHT // 2 - text.get_height() // 2) // 4
        #     surface.blit(text, (x, y))

        #     if dt > 3000:
        #         text = pygame.font.Font("chalk.ttf", 42).render(
        #             "Left Click to Start", True, (c, c, c)
        #         )
        #         x = SCREEN_WIDTH // 2 - text.get_width() // 2
        #         y = 3 * SCREEN_HEIGHT // 4
        #         surface.blit(text, (x, y))

        # def eventloop(self, game):
        #     for event in pygame.event.get():
        #         if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
        #             pygame.quit()
        #             sys.exit()
        #         elif event.type == pygame.MOUSEBUTTONUP:
        #             game.state = Game.RunningGame()


class Level:
    def __init__(self, n):
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        ball = Ball()
        self.balls.add(ball)
        self.paddle.attached_balls.add(ball)
        self.bonuses = pygame.sprite.Group()

        self.tile_matrix = [[None for _ in range(20)] for _ in range(20)]
        self.tiles = pygame.sprite.Group()
        for line in open(os.path.join("levels", f"{n}.txt")):
            alias, i, j, *args = line.split()
            if alias not in Tile.types:
                raise RuntimeError("invalid tile type")
            i, j = int(i), int(j)
            tile = Tile.types[alias](MARGIN + 60 * i, 3 * MARGIN + 30 * j, *args)
            self.tile_matrix[i][j] = tile
            self.tiles.add(tile)

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
    
    def explosion(self, i, j):
        for k in range(-1, 2):
            for l in range(-1, 2):
                try:
                    tile = self.tile_matrix[i + k][j + l]
                    if tile.alive():
                        tile.kill()
                except (AttributeError, IndexError):
                    pass

    def on_death(self):
        time.sleep(1)

        # refresh paddle, ball, delete bonuses
        self.paddle = Paddle()
        self.balls.empty()
        ball = Ball()
        self.balls.add(ball)
        self.paddle.attached_balls.add(ball)
        self.bonuses.empty()

        # reset bonuses
        Ball.is_bullet = False
