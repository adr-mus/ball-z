import os.path

import pygame


class Explosion(pygame.sprite.Sprite):
    images = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "explosion", f"{i}.png"))) for i in range(1, 7)]
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = pygame.time.get_ticks()

    def update(self):
        dt = pygame.time.get_ticks() - self.timer
        i = int(6 * dt // 250)
        if i < len(self.images):
            self.image = self.images[i]
        else:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
