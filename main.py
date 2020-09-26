
import numpy as np


class Ball:
    h = 0.1
    is_tiny = False
    is_fiery = False
    is_bullet = False

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
    
    def update_xy(self):
        self.x += self.vx * self.h
        self.y += self.vy * self.h
    

class Paddle:
    LENGTHS = [2, 5, 10, 15, 22, 32]
    def __init__(self):
        self.l = 2
        self.x = 0

        self.shoots = False
        self.is_magnetic = False
        self.is_cursed = False
    
    @property
    def length(self):
        return self.LENGTHS[self.l]
    
    def update_x(self):
        pass

    def hit(self, dx, ball):
        pass


class Level:
    def __init__(self, i):
        self.tiles = np.load(f"levels\\lvl_{i}.npy")
        self.paddle = Paddle()
        self.balls = [Ball()]


class Game:
    def __init__(self):
        self.level = Level(1)
        self.lives = 2
        self.score = 0

# resolution: 640x480
# tile size: 30x15
# level width: 20*30 = 600
# margin width: (640 - 600)/2 = 20
# level height: 20*15 = 300
# upper margin height: 3*15 + 3 = 48
# board space height: 7*15 = 105
# lower margin height: 480 - (300 + 48 + 105) = 27
# base paddle length: 72

        
