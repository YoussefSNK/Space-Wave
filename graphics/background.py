import pygame
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from resource_path import resource_path


class Background:
    def __init__(self, image_path=None, speed=2):
        self.speed = speed
        self.default_speed = speed
        if image_path:
            self.image = pygame.image.load(resource_path(image_path)).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((10, 10, 30))
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.image, WHITE, (x, y), 1)
        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))
