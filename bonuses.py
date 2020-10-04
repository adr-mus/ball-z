import abc, random, os.path

import pygame

import events
from ball import Ball
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Bonus(pygame.sprite.Sprite, abc.ABC):
    image = None  # to be specified in subclasses

    __types = []  # used for rolling
    __weights = []  # different bonuses have different probabilities

    @staticmethod  # used to dynamically add new bonuses to the pool
    def register_type(weight):
        def wrapper(subcls):
            Bonus.__types.append(subcls)
            Bonus.__weights.append(weight)
            return subcls

        return wrapper

    def __init__(self, x0, y0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(center=(x0, y0))
        self.v = random.randrange(4, 11)

    def update(self):
        self.rect.move_ip(0, self.v)
        if self.rect.top >= SCREEN_HEIGHT + MARGIN:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @classmethod
    def on_collect(cls):
        pygame.event.post(pygame.event.Event(events.POINTS, points=100))
        pygame.event.post(pygame.event.Event(events.BONUS_COLLECTED, bonus=cls))

    @classmethod
    def random_bonus(cls, x0, y0):
        # cls.game.lvl.bonuses.add(Soften(x0, y0))
        bonus = random.choices(cls.__types, cls.__weights)[0](x0, y0)
        pygame.event.post(pygame.event.Event(events.BONUS_DROPPED, bonus=bonus))


############ general ############
@Bonus.register_type(3)
class Death(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "death.png"))

    @staticmethod
    def take_effect(game):
        game.on_death()


@Bonus.register_type(2)
class Life(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "life.png"))

    @staticmethod
    def take_effect(game):
        if game.lives == 4:
            game.score += 900
        else:
            game.lives += 1


# @Bonus.register_type(1)
# class NextLevel(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.on_win()


@Bonus.register_type(4)
class Soften(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "soften.png"))

    @staticmethod
    def take_effect(game):
        for tile in game.lvl.tiles:
            tile.soften()


# @Bonus.register_type(4)
# class Explode(Bonus):
#     @classmethod
# def on_collect(cls):
#         for tile in cls.game.level.tiles:
#             if isinstance(tile, ExplosiveTile):
#                 tile.explode()


# @Bonus.register_type(3)
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
# @Bonus.register_type(4)
# class SpeedUp(Bonus):
#     @classmethod
# def on_collect(cls):
#         for ball in cls.game.level.balls:
#             ball.update_v(2)


# @Bonus.register_type(4)
# class SlowDown(Bonus):
#     @classmethod
# def on_collect(cls):
#         for ball in cls.game.level.balls:
#             ball.reset_v()


@Bonus.register_type(3)
class Bullet(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "bullet.png"))

    @staticmethod
    def take_effect(game):
        Ball.is_bullet = True


# @Bonus.register_type(3)
# class FireBall(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.balls[0].__class__.is_fiery = True


# @Bonus.register_type(3)
# class TinyBall(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.balls[0].__class__.is_tiny = True


@Bonus.register_type(4)
class Split(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "split.png"))

    @staticmethod
    def take_effect(game):
        new_balls = pygame.sprite.Group()
        for ball in game.lvl.balls:
            new_ball = Ball()
            new_ball.rect.center = ball.rect.center
            new_ball.vx, new_ball.vy = -ball.vx, ball.vy
            new_balls.add(ball)
            new_balls.add(new_ball)
        game.lvl.balls = new_balls


############ paddle ############
# @Bonus.register_type(4)
# class Magnet(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.level.paddle.is_magnetic = True


# @Bonus.register_type(3)
# class Guns(Bonus):
#     @classmethod
# def on_collect(cls):
#         cls.game.level.paddle.is_shooting = True


@Bonus.register_type(5)
class Enlarge(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "enlarge.png"))

    @staticmethod
    def take_effect(game):
        paddle = game.lvl.paddle
        paddle.len = max(paddle.len + 1, 4)
        w, h = paddle.base_image.get_size()
        paddle.image = pygame.transform.scale(
            paddle.base_image, (int(w * 2 ** paddle.len), h)
        )
        paddle.rect = paddle.image.get_rect(center=paddle.rect.center)


@Bonus.register_type(5)
class Shrink(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "shrink.png"))

    @staticmethod
    def take_effect(game):
        paddle = game.lvl.paddle
        paddle.len = max(paddle.len - 1, -2)
        w, h = paddle.base_image.get_size()
        paddle.image = pygame.transform.scale(
            paddle.base_image, (int(w * 2 ** paddle.len), h)
        )
        paddle.rect = paddle.image.get_rect(center=paddle.rect.center)
