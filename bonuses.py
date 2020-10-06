import abc, random, os.path, math

import pygame

import events
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN
from ball import Ball


class Bonus(pygame.sprite.Sprite, abc.ABC):
    image = None  # to be specified in subclasses
    sounds = {"positive": pygame.mixer.Sound(os.path.join("sounds", "positive.wav")),
              "negative": pygame.mixer.Sound(os.path.join("sounds", "negative.wav"))}

    sounds["positive"].set_volume(0.1)
    sounds["negative"].set_volume(0.1)

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
        # bonus = Explode(x0, y0)
        bonus = random.choices(cls.__types, cls.__weights)[0](x0, y0)
        pygame.event.post(pygame.event.Event(events.BONUS_DROPPED, bonus=bonus))


############ general ############
@Bonus.register_type(3)
class Death(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "death.png"))

    @classmethod
    def take_effect(cls, game):
        game.on_death()


@Bonus.register_type(2)
class Life(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "life.png"))
    sound = pygame.mixer.Sound(os.path.join("sounds", "life.wav"))

    @classmethod
    def take_effect(cls, game):
        cls.sound.play()
        if game.lives == 4:
            game.score += 900
        else:
            game.lives += 1


@Bonus.register_type(4)
class Explode(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "explode.png"))

    @classmethod
    def take_effect(cls, game):
        from tiles import ExplosiveTile, UnstableTile

        cls.sounds["positive"].play()
        for tile in game.lvl.tiles:
            if isinstance(tile, ExplosiveTile) or isinstance(tile, UnstableTile) and tile.hit:
                tile.kill()


############ ball ############
@Bonus.register_type(4)
class SpeedUp(Bonus):
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
    image = pygame.image.load(os.path.join("images", "bonuses", "fireball.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        Ball.is_fiery = True


@Bonus.register_type(3)
class Tiny(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "tiny.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        w, h = Ball.base_image.get_size()
        Ball.image = pygame.transform.scale(
            Ball.base_image, (w // 2, h // 2)
        )
        for ball in game.lvl.balls:
            ball.rect = ball.image.get_rect(center=ball.rect.center)


@Bonus.register_type(4)
class Split(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "split.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        new_balls = pygame.sprite.Group()
        for ball in game.lvl.balls:
            new_ball = Ball()
            new_ball.is_attached = False
            new_ball.rect.center = ball.rect.center
            new_ball.vx, new_ball.vy = -ball.vx, ball.vy
            new_balls.add(ball)
            new_balls.add(new_ball)
        game.lvl.balls = new_balls


############ paddle ############
@Bonus.register_type(4)
class Magnet(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "magnet.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        game.lvl.paddle.is_magnetic = True


@Bonus.register_type(5)
class Enlarge(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "enlarge.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["positive"].play()
        paddle = game.lvl.paddle
        paddle.len = min(paddle.len + 1, 4)
        w, h = paddle.base_image.get_size()
        paddle.image = pygame.transform.scale(
            paddle.base_image, (int(w * 2 ** paddle.len), h)
        )
        paddle.rect = paddle.image.get_rect(center=paddle.rect.center)


@Bonus.register_type(5)
class Shrink(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "shrink.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        paddle = game.lvl.paddle
        paddle.len = max(paddle.len - 1, -2)
        w, h = paddle.base_image.get_size()
        paddle.image = pygame.transform.scale(
            paddle.base_image, (int(w * 2 ** paddle.len), h)
        )
        paddle.rect = paddle.image.get_rect(center=paddle.rect.center)


@Bonus.register_type(5)
class Confuse(Bonus):
    image = pygame.image.load(os.path.join("images", "bonuses", "confuse.png"))

    @classmethod
    def take_effect(cls, game):
        cls.sounds["negative"].play()
        game.lvl.paddle.is_confused = True
        