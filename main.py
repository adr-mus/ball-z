import sys, math

# import numpy as np
import pygame
from pygame.locals import *


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class clr:
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


class Ball(pygame.sprite.Sprite):
    MAXSPEED = 15

    image = pygame.image.load(r"images\ball.png")
    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.surf = pygame.Surface((8, 8))
        self.rect = self.surf.get_rect(center=(50, 120))

        self.vx = -4
        self.vy = 1

        self.is_attached = False

    def update(self):
        if not self.is_attached:
            self.rect.move_ip(self.vx, self.vy)

            if self.rect.left < 20 or self.rect.right > 620:
                self.vx = -self.vx
            elif self.rect.top < 27:
                self.vy = -self.vy

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_v(self, alpha, factor):
        v_mag = math.sqrt(self.vx ** 2 + self.vy ** 2)
        v_mag = min(self.MAXSPEED, v_mag * factor)

        if v_mag == self.MAXSPEED:
            print("max")

        self.vx = round(v_mag * math.cos(alpha))
        self.vy = -round(v_mag * max(math.sin(alpha), 0.1))


class Paddle(pygame.sprite.Sprite):
    LENGTHS = [36, 72, 144, 288, 400]

    image = pygame.image.load(r"images\paddle.png")

    shoots = False
    is_magnetic = False
    is_cursed = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.len = 1
        self.surf = pygame.Surface((len(self), 30))
        self.rect = self.surf.get_rect(center=(320, 450))

        self.attached_to = None

    def __len__(self):
        return self.LENGTHS[self.len]

    def update(self):
        dx = pygame.mouse.get_rel()[0]
        self.rect.move_ip(dx, 0)
        if self.rect.left < 20:
            self.rect.left = 20
        elif self.rect.right > 620:
            self.rect.right = 620
        elif self.attached_to is not None:
            self.atached_to.rect.move_ip(dx, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def hit(self, ball):
        paddle_x = self.rect.center[0]
        ball_x = ball.rect.center[0]

        alpha = -math.pi * (ball_x - paddle_x) / len(self) + math.pi / 2
        ball.update_v(alpha, 1.1)


class Level:
    def __init__(self, i):
        # self.tiles = np.load(f"levels\\lvl_{i}.npy")
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())

    def update(self, surface):
        self.paddle.update()
        self.balls.update()

        self.paddle.draw(surface)
        self.balls.draw(surface)

        for ball in pygame.sprite.spritecollide(self.paddle, self.balls, 0):
            self.paddle.hit(ball)


class Game:
    def __init__(self):
        self.level = 1
        self.lvl = Level(self.level)
        self.lives = 2
        self.score = 0


if __name__ == "__main__":
    pygame.init()

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Example")

    clock = pygame.time.Clock()

    game = Game()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        for event in pygame.event.get():
            pressed = pygame.key.get_pressed()
            if event.type == QUIT or pressed[K_ESCAPE]:
                pygame.quit()
                sys.exit()

        surface.fill(clr.BLACK)

        pygame.draw.line(surface, clr.WHITE, (19, 0), (19, 479))
        pygame.draw.line(surface, clr.WHITE, (621, 0), (621, 479))

        game.lvl.update(surface)

        pygame.display.flip()

        clock.tick(60)

# resolution: 640x480
# tile size: 30x15
# level width: 20*30 = 600
# margin width: (640 - 600)/2 = 20
# level height: 20*15 = 300
# upper margin height: 3*15 + 3 = 48
# board space height: 7*15 = 105
# lower margin height: 480 - (300 + 48 + 105) = 27
# base paddle length: 72
