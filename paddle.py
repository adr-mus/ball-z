import math, os.path

import pygame

from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Paddle(pygame.sprite.Sprite):
    base_image = pygame.image.load(os.path.join("images", "paddle.png"))

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.len = 0
        self.image = self.base_image
        self.rect = self.image.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)
        )

        self.shoots = False
        self.is_magnetic = False

        self.attached_to = None

    def __len__(self):
        return self.rect.width

    def update(self):
        dx = pygame.mouse.get_rel()[0]
        self.rect.move_ip(dx, 0)
        if self.rect.left <= MARGIN:
            self.rect.left = MARGIN
        elif self.rect.right >= SCREEN_WIDTH - MARGIN:
            self.rect.right = SCREEN_WIDTH - MARGIN
        elif self.attached_to is not None:
            self.atached_to.rect.move_ip(dx, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
