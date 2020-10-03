import math, os.path

import pygame

from main import SCREEN_WIDTH, SCREEN_HEIGHT, MARGIN


class Paddle(pygame.sprite.Sprite):
    images = {i: pygame.image.load(os.path.join("images", "paddles", f"{i}.png"))
                for i in range(5)}

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.len = 1
        self.image = self.images[self.len]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN))

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

    def hit(self, ball):
        paddle_x = self.rect.center[0]
        ball_x = ball.rect.center[0]

        alpha = -math.pi * (ball_x - paddle_x) / len(self) + math.pi / 2
        ball.update_v(alpha)
    
    def enlarge(self, negative=False):
        self.len = max(self.len - 1, 0) if negative else min(self.len + 1, 4)
        self.image = self.images[self.len]
        self.rect = self.image.get_rect(center=self.rect.center)
