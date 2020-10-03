import abc, random, os.path

import pygame

from ball import Ball
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Bonus(pygame.sprite.Sprite, abc.ABC):
    game = None # backreference to the game - so that bonuses can take effect
    p = 1 # the probability of rolling a bonus

    image = None # to be specified in subclasses

    __bonuses = [] # used for rolling -
    __weights = [] # different bonuses have different probabilities
    @staticmethod  # used to dynamically add new bonuses to the pool
    def register_bonus(weight):
        def wrapper(subcls):
            Bonus.__bonuses.append(subcls)
            Bonus.__weights.append(weight)
            return subcls

        return wrapper

    def __init__(self, x0, y0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(center=(x0, y0))
        self.v = random.randrange(3, 7)

    def update(self):
        self.rect.move_ip(0, self.v)
        if self.rect.top > SCREEN_HEIGHT + MARGIN:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @classmethod
    def on_collect(cls): # TO BE EXTENDED Or OVERLOADED IN SUBCLASSES
        cls.game.score += 100
    
    @classmethod
    def random_bonus(cls, x0, y0):
        # if random.random() < cls.p:
        # cls.game.lvl.bonuses.add(Soften(x0, y0))
        cls.game.lvl.bonuses.add(random.choices(Bonus.__bonuses, Bonus.__weights)[0](x0, y0))


############ general ############
@Bonus.register_bonus(3)
class Death(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "death.png"))
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        cls.game.on_death()


@Bonus.register_bonus(2)
class Life(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "life.png"))
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        if cls.game.lives == 4:
            cls.game.score += 900
        else:    
            cls.game.lives += 1


# @Bonus.register_bonus(1)
# class NextLevel(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.on_win()


@Bonus.register_bonus(4)
class Soften(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "soften.png")) 
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        for tile in cls.game.lvl.tiles:
            tile.soften()


# @Bonus.register_bonus(4)
# class Explode(Bonus):
#     @classmethod
# def on_collect(cls):
#         for tile in cls.game.level.tiles:
#             if isinstance(tile, ExplosiveTile):
#                 tile.explode()


# @Bonus.register_bonus(3)
# class MultiplyExplosives(Bonus):
#     @classmethod
# def on_collect(cls):
#         n, k = cls.game.level.tiles.shape
#         for i in range(n):
#             for j in range(k):
#                 if isinstance(cls.game.level.tiles[i, j], ExplosiveTile):
#                     if i >= 1:
#                         cls.game.level.tiles[i - 1, j] = ExplosiveTile()
#                     if j >= 1:
#                         cls.game.level.tiles[i, j - 1] = ExplosiveTile()
#                     if i < n - 1:
#                         cls.game.level.tiles[i + 1, j] = ExplosiveTile()
#                     if j < k - 1:
#                         cls.game.level.tiles[i, j + 1] = ExplosiveTile()


############ ball ############
# @Bonus.register_bonus(4)
# class SpeedUp(Bonus):
#     @classmethod
# def on_collect(cls):
#         for ball in cls.game.level.balls:
#             ball.update_v(2)


# @Bonus.register_bonus(4)
# class SlowDown(Bonus):
#     @classmethod
# def on_collect(cls):
#         for ball in cls.game.level.balls:
#             ball.reset_v()


@Bonus.register_bonus(3)
class Bullet(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "bullet.png")) 
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        Ball.is_bullet = True


# @Bonus.register_bonus(3)
# class FireBall(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.balls[0].__class__.is_fiery = True


# @Bonus.register_bonus(3)
# class TinyBall(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.balls[0].__class__.is_tiny = True


# @Bonus.register_bonus(4)
# class SplitBall(Bonus):
#     @classmethod
# def on_collect(cls):
#         new_balls = []
#         for ball in cls.game.level.balls:
#             new_balls.append(ball)
#             new_balls.append(ball.mirror_image())
#         cls.game.level.balls = new_balls


############ paddle ############
# @Bonus.register_bonus(4)
# class Magnet(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.level.paddle.is_magnetic = True


# @Bonus.register_bonus(3)
# class Guns(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.level.paddle.is_shooting = True


@Bonus.register_bonus(5)
class Enlarge(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "enlarge.png")) 
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        cls.game.lvl.paddle.enlarge()


@Bonus.register_bonus(5)
class Shrink(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "shrink.png"))
    @classmethod
    def on_collect(cls):
        Bonus.on_collect()
        cls.game.lvl.paddle.enlarge(negative=True)


