import abc, random, os.path

import pygame

# from tiles import ExplosiveTile


class Bonus(pygame.sprite.Sprite, abc.ABC):
    game = None # backreference to the game - so that bonuses can take effect
    p = 1 # the probability of rolling a bonus
    __bonuses = [] # used for rolling -
    __weights = [] # different bonuses have different probabilities

    # used to dynamically add new bonuses to the pool
    @staticmethod
    def register_bonus(weight):
        def wrapper(subcls):
            Bonus.__bonuses.append(subcls)
            Bonus.__weights.append(weight)
            return subcls

        return wrapper

    def __init__(self, x0, y0):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((30, 30))
        self.rect = self.surf.get_rect(center=(x0, y0))
        self.v = random.randrange(1, 8)

    def update(self):
        self.rect.move_ip(0, self.v)
        if self.rect.top > 485:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @abc.abstractmethod
    def on_collect(self):
        pass
    
    @classmethod
    def random_bonus(cls, x0, y0):
        if random.random() < cls.p:
            cls.game.lvl.bonuses.add(Longer(x0, y0))
            # cls.game.lvl.bonuses.add(random.choices(Bonus.__bonuses, Bonus.__weights)[0](x0, y0))


############ general ############
@Bonus.register_bonus(3)
class Death(Bonus):
    def on_collect(self):
        self.game.on_death()


@Bonus.register_bonus(2)
class Life(Bonus):
    def on_collect(self):
        self.game.lives = min(self.game.lives + 1, 4)


@Bonus.register_bonus(1)
class NextLevel(Bonus):
    def on_collect(self):
        self.game.on_win()


@Bonus.register_bonus(4)
class Soften(Bonus):
    def on_collect(self):
        for tile in self.game.lvl.tiles:
            tile.soften()


# @Bonus.register_bonus(4)
# class Explode(Bonus):
#     def on_collect(self):
#         for tile in self.game.level.tiles:
#             if isinstance(tile, ExplosiveTile):
#                 tile.explode()


# @Bonus.register_bonus(3)
# class MultiplyExplosives(Bonus):
#     def on_collect(self):
#         n, k = self.game.level.tiles.shape
#         for i in range(n):
#             for j in range(k):
#                 if isinstance(self.game.level.tiles[i, j], ExplosiveTile):
#                     if i >= 1:
#                         self.game.level.tiles[i - 1, j] = ExplosiveTile()
#                     if j >= 1:
#                         self.game.level.tiles[i, j - 1] = ExplosiveTile()
#                     if i < n - 1:
#                         self.game.level.tiles[i + 1, j] = ExplosiveTile()
#                     if j < k - 1:
#                         self.game.level.tiles[i, j + 1] = ExplosiveTile()


############ ball ############
@Bonus.register_bonus(4)
class SpeedUp(Bonus):
    def on_collect(self):
        for ball in self.game.level.balls:
            ball.update_v(2)


@Bonus.register_bonus(4)
class SlowDown(Bonus):
    def on_collect(self):
        for ball in self.game.level.balls:
            ball.reset_v()


@Bonus.register_bonus(3)
class Bullet(Bonus):
    def on_collect(self):
        for ball in self.game.level.balls:
            ball.is_bullet = True


@Bonus.register_bonus(3)
class FireBall(Bonus):
    def on_collect(self):
        self.game.balls[0].__class__.is_tiny = True


@Bonus.register_bonus(3)
class TinyBall(Bonus):
    def on_collect(self):
        self.game.balls[0].__class__.is_tiny = True


@Bonus.register_bonus(4)
class SplitBall(Bonus):
    def on_collect(self):
        new_balls = []
        for ball in self.game.level.balls:
            new_balls.append(ball)
            new_balls.append(ball.mirror_image())
        self.game.level.balls = new_balls


############ paddle ############
@Bonus.register_bonus(4)
class Magnet(Bonus):
    def on_collect(self):
        self.game.level.paddle.is_magnetic = True


@Bonus.register_bonus(3)
class Guns(Bonus):
    def on_collect(self):
        self.game.level.paddle.is_shooting = True


@Bonus.register_bonus(5)
class Longer(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "enlarge.png")) 
    def on_collect(self):
        self.game.lvl.paddle.enlarge()


@Bonus.register_bonus(5)
class Shorter(Bonus):
    def on_collect(self):
        self.game.paddle.shorten(1)


@Bonus.register_bonus(3)
class Shrink(Bonus):
    def on_collect(self):
        self.game.paddle.shorten()


@Bonus.register_bonus(3)
class Fall(Bonus):
    def on_collect(self):
        self.game.level.paddle.cursed = True
