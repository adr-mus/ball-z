import math, os.path

import pygame

class Paddle(pygame.sprite.Sprite):
    LENGTHS = [36, 72, 144, 288, 400]

    image = pygame.image.load(os.path.join("images", "paddles", "1.png"))

    shoots = False
    is_magnetic = False
    is_cursed = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.len = 1
        self.surf = pygame.Surface((len(self), 2))
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
        ball.update_v(alpha, 1)
    
    def enlarge(self):
        pass
