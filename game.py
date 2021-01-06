""" Module defining the high-level Game class. """

import time
import os
import sys 
import math 
import pickle

import pygame

import events
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN
from fonts import *
from level import Level


class Game:
    """ Proxy class representing a game. Relegates everything to self.state 
        which represents a concrete state of a game: start screen, running 
        game, transition from running game to ranking, or ranking. Event loops 
        are used to change the state attribute. """
    music = pygame.mixer.Sound(os.path.join("sounds", "menu.wav"))
    ranking_path = os.path.join("misc", "rank.pkl")
    
    def __init__(self, *, start_lvl=1):
        self.state = Game.StartScreen()
        self.start_lvl = start_lvl

    def draw(self, surface):
        """ Draws the current state of a game. """
        self.state.draw(surface)

    def update(self):
        """ Updates the state of all changing elements of self. state
            (e.g. music, sprites, collisions). """
        self.state.update()

    def eventloop(self):
        self.state.eventloop(self)

    class StartScreen:
        def __init__(self):
            self.timer = pygame.time.get_ticks()
            if not pygame.mixer.get_busy():
                self.base_volume = 0
                Game.music.play(loops=-1)
            else:
                self.base_volume = Game.music.get_volume()

        def draw(self, surface):
            # background
            surface.fill(pygame.Color("black"))

            # get time
            dt = pygame.time.get_ticks() - self.timer

            # title
            c = min(int(255 * dt / 2000), 255)
            text = title_font.render("BALL-Z", True, (c, c, c))
            x = SCREEN_WIDTH // 2 - text.get_width() // 2
            y = (SCREEN_HEIGHT // 2 - text.get_height() // 2) // 2
            surface.blit(text, (x, y))

            # instruction
            if dt > 2000:
                c = 150 + int(100 * math.sin((dt - 2000 - 250*math.pi) / 500))
                text = regular_font.render("Left Click to Start", True, (c, c, c))
                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                y = 3 * SCREEN_HEIGHT // 4
                surface.blit(text, (x, y))

        def update(self):
            # volume
            dt = pygame.time.get_ticks() - self.timer
            Game.music.set_volume(self.base_volume + (dt / 6000) ** 2)

        def eventloop(self, game):
            pygame.mouse.get_rel()
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        game.state = Game.Ranking()
                elif event.type == pygame.MOUSEBUTTONUP:
                    Game.music.fadeout(1000)
                    game.state = Game.RunningGame(game.start_lvl)

    class RunningGame:
        margin = pygame.image.load(os.path.join("images", "margin.png"))

        def __init__(self, start_lvl=1):
            self.n_lvl = start_lvl # the current level number
            self.lvl = Level(self.n_lvl) # the current level object
            self.lives = 2 # lives left
            self.score = 0 # points

        def draw(self, surface):
            # background
            surface.fill(pygame.Color("black"))

            # margins
            surface.blit(self.margin, (MARGIN - 30, 0))
            surface.blit(self.margin, (SCREEN_WIDTH - MARGIN, 0))

            # lives
            if self.lives > 0:
                lives = "I" * self.lives
                text = regular_font.render(lives, True, pygame.Color("white"))
                surface.blit(text, (SCREEN_WIDTH - MARGIN - 10 - text.get_width(), 1))

            # score
            text = regular_font.render(str(self.score), True, pygame.Color("white"))
            surface.blit(text, (MARGIN + 10, 1))

            # balls, tiles, paddle, bonuses
            self.lvl.draw(surface)

        def update(self):
            self.lvl.update()

        def on_death(self):
            """ Triggered when player loses all balls. """
            self.lvl.on_death()
            self.lives -= 1
            if self.lives < 0:
                pygame.event.post(pygame.event.Event(events.GAME_OVER, won=False))

        def next_level(self):
            """ Triggered when player finishes the current level. """
            self.n_lvl += 1
            try:
                self.lvl = Level(self.n_lvl)
            except FileNotFoundError:
                pygame.event.post(pygame.event.Event(events.GAME_OVER, won=True))

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        game.state = Game.StartScreen()
                    elif not self.lvl.finished and event.key == pygame.K_p:
                        self.lvl.paused = not self.lvl.paused
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.lvl.finished:
                        self.next_level()
                    else:
                        for ball in self.lvl.paddle.attached_balls:
                            ball.on_hit(self.lvl.paddle)
                        self.lvl.paddle.attached_balls.clear()
                elif event.type == events.BONUS_DROPPED:
                    self.lvl.bonuses.add(event.bonus)
                elif event.type == events.BONUS_COLLECTED:
                    event.bonus.take_effect(self)
                elif event.type == events.POINTS:
                    self.score += event.points
                elif event.type == events.EXPLOSION:
                    self.lvl.explosion(*event.where)
                elif event.type == events.DEATH:
                    self.on_death()
                elif event.type == events.GAME_OVER:
                    final_score = self.score + (self.n_lvl - 1) * 1000
                    game.state = Game.RankingTransition(final_score, won=event.won)

    class RankingTransition:
        def __init__(self, score, won):
            self.score = score
            self.title = "All Levels Cleared!" if won else "Good Luck Next Time!"
            try:
                with open(Game.ranking_path, "rb") as f:
                    self.ranking = pickle.load(f)
            except (FileNotFoundError, EOFError):
                self.ranking = []
                self.ask_name = True
            else:
                self.ask_name = len(self.ranking) < 5 or self.ranking[-1][1] < self.score
            self.name = ""

            self.timer = pygame.time.get_ticks()
            Game.music.play(loops=-1)

        def draw(self, surface):
            # background
            surface.fill(pygame.Color("black"))

            # time
            dt = pygame.time.get_ticks() - self.timer

            # title
            c = min(int(255 * dt / 3000), 255)
            text = message_font.render(self.title, True, (c, c, c))
            x = (SCREEN_WIDTH - text.get_width()) // 2
            y = (SCREEN_HEIGHT - text.get_height()) // 8
            surface.blit(text, (x, y))
            
            if dt > 3000:
                text = regular_font.render("Final Score:", True, pygame.Color("white"))
                x = (SCREEN_WIDTH - text.get_width()) // 4
                y = (SCREEN_HEIGHT - text.get_height()) // 3 + 100
                surface.blit(text, (x, y))
            
            if dt > 3500:
                text = regular_font.render(str(self.score), True, pygame.Color("white"))
                x = 2 * SCREEN_WIDTH // 3
                y = (SCREEN_HEIGHT - text.get_height()) // 3 + 100
                surface.blit(text, (x, y))

            if dt > 4000: 
                if self.ask_name:
                    text = regular_font.render("Your Name", True, pygame.Color("white"))
                    x = (SCREEN_WIDTH - text.get_width()) // 4
                    y = 2 * (SCREEN_HEIGHT - text.get_height()) // 3
                    surface.blit(text, (x, y))

                    text = regular_font.render(self.name, True, pygame.Color("white"))
                    x = 2 * SCREEN_WIDTH // 3
                    y = 2 * (SCREEN_HEIGHT - text.get_height()) // 3
                    surface.blit(text, (x, y))

                    col = pygame.Color("black") if (dt // 500) % 2 == 0 else pygame.Color("white")
                    dot = regular_font.render(".", True, col)
                    x = 2 * SCREEN_WIDTH // 3 + text.get_width() + dot.get_width()
                    y = 2 * (SCREEN_HEIGHT - text.get_height()) // 3
                    surface.blit(dot, (x, y))
                else:
                    time.sleep(1)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

        def update(self):
            # volume
            dt = pygame.time.get_ticks() - self.timer
            Game.music.set_volume((dt / 6000) ** 2)

        def update_ranking(self):
            self.ranking.append((self.name, self.score))
            self.ranking.sort(key=lambda el: el[1], reverse=True)
            while len(self.ranking) > 5:
                self.ranking.pop()
            with open(Game.ranking_path, "wb") as f:
                pickle.dump(self.ranking, f)

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        Game.music.fadeout(1000)
                        game.state = Game.StartScreen()
                    elif self.ask_name:
                        if event.key == pygame.K_BACKSPACE:
                            self.name = self.name[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.update_ranking()
                            game.state = Game.Ranking()
                        else:
                            if len(self.name) < 8:
                                self.name += event.unicode

    class Ranking:
        def __init__(self):
            try:
                with open(Game.ranking_path, "rb") as f:
                    self.ranking = pickle.load(f)
            except (FileNotFoundError, EOFError):
                self.ranking = []
            self.drawn = False

            self.timer = pygame.time.get_ticks()
            if not pygame.mixer.get_busy():
                self.base_volume = 0
                Game.music.play(loops=-1)
            else:
                self.base_volume = Game.music.get_volume()

        def update(self):
            # volume
            dt = pygame.time.get_ticks() - self.timer
            Game.music.set_volume(self.base_volume + (dt / 6000) ** 2)

        def draw(self, surface):
            if not self.drawn:
                # background
                surface.fill(pygame.Color("black"))

                # title
                text = message_font.render("Best Scores", True, pygame.Color("white"))
                x = (SCREEN_WIDTH - text.get_width()) // 2
                y = 50
                surface.blit(text, (x, y))
                
                # ranking
                for i, (name, score) in enumerate(self.ranking):
                    text = regular_font.render(f"{i + 1}.", True, pygame.Color("white"))
                    x = 50
                    y = (SCREEN_HEIGHT - text.get_height()) // 3 + i * 100
                    surface.blit(text, (x, y))

                    text = regular_font.render(name, True, pygame.Color("white"))
                    x = 150
                    surface.blit(text, (x, y))

                    text = regular_font.render(str(score), True, pygame.Color("white"))
                    x = SCREEN_WIDTH - text.get_width() - 50
                    surface.blit(text, (x, y))
                
                self.drawn = True

        def eventloop(self, game):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP and (event.key == pygame.K_ESCAPE or event.key == pygame.K_r):
                    game.state = Game.StartScreen()
