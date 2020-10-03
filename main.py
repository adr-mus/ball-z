import sys

import pygame
from pygame.locals import *

from game import Game


def event_loop():
    for event in pygame.event.get():
        if event.type == KEYUP and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    pygame.init()

    surface = pygame.display.set_mode((640, 480), FULLSCREEN)
    pygame.display.set_caption("Ball-Z")

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    clock = pygame.time.Clock()

    game = Game()
    while True:
        event_loop()

        game.update()
        game.draw(surface)

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
