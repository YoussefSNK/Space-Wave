import pygame

from config import RED
from .projectiles import EnemyProjectile


class Enemy:
    def __init__(self, x, y, speed=3, movement_pattern=None):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hp = 2
        self.movement_pattern = movement_pattern
        self.timer = 0
        self.start_x = x
        self.start_y = y
        self.drops_powerup = False

    def update(self):
        self.timer += 1
        if self.movement_pattern:
            self.movement_pattern.update(self)
        else:
            self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class ShootingEnemy(Enemy):
    def __init__(self, x, y, speed=3, shoot_delay_frames=60):
        super().__init__(x, y, speed)
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.shoot_delay_frames = shoot_delay_frames
        self.last_shot_frame = 0

    def _create_sprite(self):
        """Crée le sprite du ShootingEnemy - un drone ennemi agressif"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Couleurs
        body_color = (180, 30, 180)  # Magenta foncé
        body_highlight = (220, 80, 220)  # Magenta clair
        eye_color = (255, 50, 50)  # Rouge vif pour l'oeil/canon
        wing_color = (120, 20, 120)  # Violet foncé pour les ailes
        outline_color = (80, 10, 80)  # Contour sombre

        center_x, center_y = size // 2, size // 2

        # Corps principal - hexagone aplati (forme de drone)
        body_points = [
            (center_x, center_y - 12),      # Haut
            (center_x + 10, center_y - 6),  # Haut droite
            (center_x + 10, center_y + 6),  # Bas droite
            (center_x, center_y + 12),      # Bas
            (center_x - 10, center_y + 6),  # Bas gauche
            (center_x - 10, center_y - 6),  # Haut gauche
        ]
        pygame.draw.polygon(surface, body_color, body_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Ailes latérales (triangles pointant vers l'extérieur)
        # Aile gauche
        left_wing = [
            (center_x - 10, center_y - 4),
            (center_x - 18, center_y),
            (center_x - 10, center_y + 4),
        ]
        pygame.draw.polygon(surface, wing_color, left_wing)
        pygame.draw.polygon(surface, outline_color, left_wing, 1)

        # Aile droite
        right_wing = [
            (center_x + 10, center_y - 4),
            (center_x + 18, center_y),
            (center_x + 10, center_y + 4),
        ]
        pygame.draw.polygon(surface, wing_color, right_wing)
        pygame.draw.polygon(surface, outline_color, right_wing, 1)

        # Highlight sur le corps (reflet)
        highlight_points = [
            (center_x, center_y - 10),
            (center_x + 6, center_y - 5),
            (center_x + 6, center_y),
            (center_x, center_y + 2),
            (center_x - 6, center_y),
            (center_x - 6, center_y - 5),
        ]
        pygame.draw.polygon(surface, body_highlight, highlight_points)

        # Oeil central / Canon - cercle rouge menaçant
        pygame.draw.circle(surface, eye_color, (center_x, center_y + 2), 5)
        pygame.draw.circle(surface, (255, 150, 150), (center_x - 1, center_y + 1), 2)  # Reflet

        # Canon/Nez pointant vers le bas (direction de tir)
        cannon_points = [
            (center_x - 3, center_y + 12),
            (center_x, center_y + 18),
            (center_x + 3, center_y + 12),
        ]
        pygame.draw.polygon(surface, eye_color, cannon_points)

        return surface

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        if self.timer < 120:
            self.rect.y += self.speed
        else:
            if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                self.last_shot_frame = self.timer
                proj = self.shoot(player_position)
                enemy_projectiles.append(proj)

    def shoot(self, player_position):
        ex, ey = self.rect.center
        px, py = player_position
        dx = px - ex
        dy = py - ey
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            dist = 1
        dx /= dist
        dy /= dist
        return EnemyProjectile(ex, ey, dx, dy, speed=7)
