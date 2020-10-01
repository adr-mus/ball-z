import abc, random

from tiles import ExplosiveTile


class Bonus(abc.ABC):
    __bonuses = []
    __weights = []

    @staticmethod
    def register_bonus(weight):
        def wrapper(subcls):
            Bonus.__bonuses.append(subcls)
            Bonus.__weights.append(weight)
            return subcls

        return wrapper

    def __init__(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        self.vx = 0
        self.vy = 0

    def update_xy(self):
        pass

    @abc.abstractmethod
    def on_collect(self, game):
        pass

    @staticmethod
    def random_bonus(x0, y0):
        if random.random() > 0.8:
            return random.choices(Bonus.__bonuses, Bonus.__weights)[0](x0, y0)


############ general ############
@Bonus.register_bonus(3)
class Death(Bonus):
    def on_collect(self, game):
        game.on_death()


@Bonus.register_bonus(2)
class Life(Bonus):
    def on_collect(self, game):
        game.lives = min(game.lives + 1, 4)


@Bonus.register_bonus(1)
class NextLevel(Bonus):
    def on_collect(self, game):
        game.on_win()


@Bonus.register_bonus(4)
class Soften(Bonus):
    def on_collect(self, game):
        for tile in game.level.tiles:
            try:
                tile.soften()
            except AttributeError:
                pass


@Bonus.register_bonus(4)
class Explode(Bonus):
    def on_collect(self, game):
        for tile in game.level.tiles:
            if isinstance(tile, ExplosiveTile):
                tile.explode()


@Bonus.register_bonus(3)
class MultiplyExplosives(Bonus):
    def on_collect(self, game):
        n, k = game.level.tiles.shape
        for i in range(n):
            for j in range(k):
                if isinstance(game.level.tiles[i, j], ExplosiveTile):
                    if i >= 1:
                        game.level.tiles[i - 1, j] = ExplosiveTile()
                    if j >= 1:
                        game.level.tiles[i, j - 1] = ExplosiveTile()
                    if i < n - 1:
                        game.level.tiles[i + 1, j] = ExplosiveTile()
                    if j < k - 1:
                        game.level.tiles[i, j + 1] = ExplosiveTile()


############ ball ############
@Bonus.register_bonus(4)
class SpeedUp(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.update_v(2)


@Bonus.register_bonus(4)
class SlowDown(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.reset_v()


@Bonus.register_bonus(3)
class Bullet(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.is_bullet = True


@Bonus.register_bonus(3)
class FireBall(Bonus):
    def on_collect(self, game):
        game.balls[0].__class__.is_tiny = True


@Bonus.register_bonus(3)
class TinyBall(Bonus):
    def on_collect(self, game):
        game.balls[0].__class__.is_tiny = True


@Bonus.register_bonus(4)
class SplitBall(Bonus):
    def on_collect(self, game):
        new_balls = []
        for ball in game.level.balls:
            new_balls.append(ball)
            new_balls.append(ball.mirror_image())
        game.level.balls = new_balls


############ paddle ############
@Bonus.register_bonus(4)
class Magnet(Bonus):
    def on_collect(self, game):
        game.level.paddle.is_magnetic = True


@Bonus.register_bonus(3)
class Guns(Bonus):
    def on_collect(self, game):
        game.level.paddle.is_shooting = True


@Bonus.register_bonus(5)
class Longer(Bonus):
    def on_collect(self, game):
        game.paddle.enlarge(1)


@Bonus.register_bonus(5)
class Shorter(Bonus):
    def on_collect(self, game):
        game.paddle.shorten(1)


@Bonus.register_bonus(3)
class Shrink(Bonus):
    def on_collect(self, game):
        game.paddle.shorten()


@Bonus.register_bonus(3)
class Fall(Bonus):
    def on_collect(self, game):
        game.level.paddle.cursed = True
