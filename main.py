MARGIN = 40
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024

FPS = 60

if __name__ == "__main__":
    import pygame

    from game import Game

    pygame.init()

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Ball-Z")

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    clock = pygame.time.Clock()

    game = Game()

    while True:
        game.eventloop()

        game.draw(surface)
        game.update()

        pygame.display.flip()
        clock.tick(FPS)
