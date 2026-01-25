import pygame
import math

from config import CYAN, WHITE


class PowerUp:
    """Power-up qui tombe et ameliore les tirs du joueur"""
    def __init__(self, x, y, power_type='double'):
        self.power_type = power_type
        self.image = pygame.Surface((30, 30))

        if power_type == 'double':
            self.color = CYAN
        elif power_type == 'triple':
            self.color = (255, 0, 255)
        elif power_type == 'spread':
            self.color = (0, 255, 100)
        elif power_type == 'ricochet':
            self.color = (255, 100, 0)
        elif power_type == 'zigzag':
            self.color = (255, 0, 200)  # Magenta
        else:
            self.color = WHITE

        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.angle = 0

    def update(self):
        self.rect.y += self.speed
        self.angle += 5

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)

        pulse = abs(math.sin(self.angle * 0.1)) * 10 + 5
        pygame.draw.circle(surface, self.color, self.rect.center, int(20 + pulse), 2)

        surface.blit(rotated, new_rect)
