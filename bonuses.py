import abc


class Bonus(abc.ABC):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

    def update_xy(self):
        pass

    @abc.abstractmethod
    def on_collect(self, game):
        pass


############ general ############
class Death(Bonus):
    def on_collect(self, game):
        game.on_death()


class Life(Bonus):
    def on_collect(self, game):
        game.lives = min(game.lives + 1, 4)


class NextLevel(Bonus):
    def on_collect(self, game):
        game.on_win()


class Soften(Bonus):
    def on_collect(self, game):
        for tile in game.level.tiles:
            try:
                tile.soften()
            except AttributeError:
                pass


class Explode(Bonus):
    def on_collect(self, game):
        for tile in game.level.tiles:
            try:
                tile.explode()
            except AttributeError:
                pass


class MultiplyExplosives(Bonus):
    pass


############ ball ############
class SpeedUp(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.update_v(2)


class SlowDown(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.reset_v()


class Bullet(Bonus):
    def on_collect(self, game):
        for ball in game.level.balls:
            ball.is_bullet = True


class FireBall(Bonus):
    def on_collect(self, game):
        game.balls[0].__class__.is_tiny = True


class TinyBall(Bonus):
    def on_collect(self, game):
        game.balls[0].__class__.is_tiny = True


class SplitBall(Bonus):
    def on_collect(self, game):
        new_balls = []
        for ball in game.level.balls:
            new_balls.append(ball)
            new_balls.append(ball.mirror_image())
        game.level.balls = new_balls


############ paddle ############
class Magnet(Bonus):
    def on_collect(self, game):
        game.level.paddle.is_magnetic = True


class Guns(Bonus):
    def on_collect(self, game):
        game.level.paddle.is_shooting = True


class Longer(Bonus):
    def on_collect(self, game):
        game.paddle.enlarge(1)


class Shorter(Bonus):
    def on_collect(self, game):
        game.paddle.shorten(1)


class Shrink(Bonus):
    def on_collect(self, game):
        game.paddle.shorten()


class Fall(Bonus):
    def on_collect(self, game):
        game.level.paddle.cursed = True
