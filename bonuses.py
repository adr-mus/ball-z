# pylint: disable=missing-function-docstring,invalid-name
""" Module defining all bonuses. """

import abc
import random
import os
import math

import pygame

import events
from main import SCREEN_HEIGHT, MARGIN
from ball import Ball


def random_bonus(x0, y0):
    """ Used to roll a bonus after a tile has been hit. """
    bonus = random.choices(Bonus.types, Bonus.weights)[0](x0, y0)
    pygame.event.post(pygame.event.Event(events.BONUS_DROPPED, bonus=bonus))


class Bonus(abc.ABC, pygame.sprite.Sprite):
    """ Base Bonus class. Each subclass must be decorated with the register_type
        method in order for the new bonus to appear in the game. This way, each
        bonus has an associated weight used later for picking a random bonus when
        a tile is hit. """
    image = None  # to be specified in subclasses
    sounds = {"positive": pygame.mixer.Sound(os.path.join("sounds", "positive.wav")),
              "negative": pygame.mixer.Sound(os.path.join("sounds", "negative.wav"))}

    # sound adjustments
    sounds["positive"].set_volume(0.1)
    sounds["negative"].set_volume(0.1)

    # used for rolling
    types = []
    weights = []

    @staticmethod
    def register_type(weight):
        """ Used as a decorator to dynamically add new bonuses to the pool. """
        def wrapper(subcls):
            Bonus.types.append(subcls)
            Bonus.weights.append(weight)
            return subcls

        return wrapper

    @classmethod
    def on_collect(cls):
        """ Triggered when a bonus is collected. """
        pygame.event.post(pygame.event.Event(events.POINTS, points=100))
        pygame.event.post(pygame.event.Event(events.BONUS_COLLECTED, bonus=cls))

    @abc.abstractclassmethod
    def take_effect(cls, game):
        """ Defines what happens when a particular bonus is collected. """

    def __init__(self, x0, y0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(center=(x0, y0))
        self.v = random.randrange(4, 9)

    def update(self):
        self.rect.move_ip(0, self.v)
        if self.rect.top >= SCREEN_HEIGHT + MARGIN:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


############ general ############
@Bonus.register_type(3)
class Death(Bonus):
    """ Immediate death. """
    image = pygame.image.load(os.path.join("images", "bonuses", "death.png"))

    @classmethod
    def take_effect(cls, game):
        game.on_death()


@Bonus.register_type(1)
class Life(Bonus):
    """ Extra life. """
    image = pygame.image.load(os.path.join("images", "bonuses", "life.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        if game.lives == 4:
            game.score += 900
        else:
            game.lives += 1


############ ball ############
@Bonus.register_type(4)
class SpeedUp(Bonus):
    """ Sets the speed of all balls to the max. """
    image = pygame.image.load(os.path.join("images", "bonuses", "speedup.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        for ball in game.lvl.balls:
            v_mag = math.hypot(ball.vx, ball.vy)
            ball.vx = int(ball.MAXSPEED * ball.vx / v_mag)
            ball.vy = int(ball.MAXSPEED * ball.vy / v_mag)


@Bonus.register_type(3)
class FireBall(Bonus):
    """ Whenever a tile is hit, it explodes. """
    image = pygame.image.load(os.path.join("images", "bonuses", "fireball.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        Ball.image = Ball.images["fiery"]
        Ball.is_fiery = True


@Bonus.register_type(4)
class Split(Bonus):
    """ Doubles the number of balls. """
    image = pygame.image.load(os.path.join("images", "bonuses", "split.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        new_balls = pygame.sprite.Group()
        for ball in game.lvl.balls:
            new_ball = Ball()
            new_ball.is_attached = ball.is_attached
            if ball.is_attached:
                game.lvl.paddle.attached_balls.add(new_ball)
            new_ball.rect.center = ball.rect.center
            new_ball.vx, new_ball.vy = -ball.vx, ball.vy
            new_balls.add(ball)
            new_balls.add(new_ball)
        game.lvl.balls = new_balls


############ paddle ############
@Bonus.register_type(4)
class Magnet(Bonus):
    """ The paddle can now capture balls and release them at will. """
    image = pygame.image.load(os.path.join("images", "bonuses", "magnet.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        paddle = game.lvl.paddle
        paddle.image = paddle.images["magnetic"]
        paddle.resize(paddle.len)
        paddle.is_magnetic = True


@Bonus.register_type(5)
class Enlarge(Bonus):
    """ Doubles the length of the paddle. """
    image = pygame.image.load(os.path.join("images", "bonuses", "enlarge.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        paddle = game.lvl.paddle
        paddle.resize(min(paddle.len + 1, 2))


@Bonus.register_type(5)
class Shrink(Bonus):
    """ Halves the length of the paddle. """
    image = pygame.image.load(os.path.join("images", "bonuses", "shrink.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        paddle = game.lvl.paddle
        paddle.resize(max(paddle.len - 1, -2))


@Bonus.register_type(4)
class Confuse(Bonus):
    """ The paddle moves in the opposite x-direction to the mouse. """
    image = pygame.image.load(os.path.join("images", "bonuses", "confuse.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        game.lvl.paddle.is_confused = not game.lvl.paddle.is_confused
        