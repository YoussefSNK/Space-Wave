import math

from config import SCREEN_WIDTH


class MovementPattern:
    """Classe de base pour les patterns de mouvement"""
    def update(self, enemy):
        pass


class SineWavePattern(MovementPattern):
    """Mouvement sinusoïdal (vague)"""
    def __init__(self, amplitude=100, frequency=0.05, base_speed=3):
        self.amplitude = amplitude
        self.frequency = frequency
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        offset_x = math.sin(enemy.timer * self.frequency) * self.amplitude
        enemy.rect.x = enemy.start_x + offset_x


class ZigZagPattern(MovementPattern):
    """Mouvement en zigzag"""
    def __init__(self, amplitude=80, switch_time=30, base_speed=3):
        self.amplitude = amplitude
        self.switch_time = switch_time
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        direction = 1 if (enemy.timer // self.switch_time) % 2 == 0 else -1
        enemy.rect.x += direction * 3


class CirclePattern(MovementPattern):
    """Mouvement circulaire"""
    def __init__(self, radius=60, angular_speed=0.08, base_speed=2):
        self.radius = radius
        self.angular_speed = angular_speed
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        angle = enemy.timer * self.angular_speed
        offset_x = math.cos(angle) * self.radius
        offset_y = math.sin(angle) * self.radius
        enemy.rect.x = enemy.start_x + offset_x
        enemy.rect.centery = enemy.start_y + (enemy.timer * self.base_speed) + offset_y


class SwoopPattern(MovementPattern):
    """Mouvement en piqué puis remontée latérale"""
    def __init__(self, swoop_direction=1):
        self.swoop_direction = swoop_direction  # 1 pour droite, -1 pour gauche
        self.phase = 0

    def update(self, enemy):
        if enemy.timer < 60:
            enemy.rect.y += 5
        elif enemy.timer < 120:
            enemy.rect.y += 2
            enemy.rect.x += self.swoop_direction * 4
        else:
            enemy.rect.y -= 1
            enemy.rect.x += self.swoop_direction * 3


class HorizontalWavePattern(MovementPattern):
    """Se déplace horizontalement avec légère descente"""
    def __init__(self, direction=1, speed=4):
        self.direction = direction
        self.speed = speed

    def update(self, enemy):
        enemy.rect.x += self.direction * self.speed
        enemy.rect.y += 1
        if enemy.rect.left <= 0 or enemy.rect.right >= SCREEN_WIDTH:
            self.direction *= -1
