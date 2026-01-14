import pygame
import math
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, RED, YELLOW, ORANGE, CYAN, WHITE


class Projectile:
    def __init__(self, x, y, speed=10):
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.trail = []
        self.max_trail_length = 6

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(1, int(4 * progress))
            color = (int(200 + 55 * progress), 255, 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.y -= self.speed

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        surface.blit(self.image, self.rect)


class SpreadProjectile(Projectile):
    """Projectile qui se deplace en diagonale pour le tir en eventail"""
    def __init__(self, x, y, speed=10, angle=15):
        super().__init__(x, y, speed)
        self.angle = angle
        angle_rad = math.radians(angle)
        self.dx = math.sin(angle_rad) * speed
        self.dy = -math.cos(angle_rad) * speed

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)


class RicochetProjectile(Projectile):
    """Projectile qui rebondit sur les ennemis dans un angle aleatoire (demi-cercle superieur)"""
    def __init__(self, x, y, speed=10, max_ricochets=2):
        super().__init__(x, y, speed)
        self.max_ricochets = max_ricochets
        self.ricochets_left = max_ricochets
        self.dx = 0
        self.dy = -1  # Commence vers le haut
        self.image.fill(ORANGE)

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def ricochet(self):
        """Change la direction du projectile apres avoir touche un ennemi.
        Retourne True si le projectile peut continuer, False sinon."""
        if self.ricochets_left <= 0:
            return False

        # Angle aleatoire dans le demi-cercle superieur (pi a 2*pi)
        angle = random.uniform(math.pi, 2 * math.pi)
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        self.ricochets_left -= 1
        return True


class EnemyProjectile:
    def __init__(self, x, y, dx, dy, speed=7):
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.trail = []
        self.max_trail_length = 5

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(1, int(3 * progress))
            color = (RED[0], RED[1], RED[2], alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        surface.blit(self.image, self.rect)


class BossProjectile(EnemyProjectile):
    """Projectiles du Boss - Plus gros et plus visibles"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((15, 15))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 8

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, int(100 + 65 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, ORANGE, self.rect.center, 7)
        pygame.draw.circle(surface, RED, self.rect.center, 5)
        pygame.draw.circle(surface, YELLOW, self.rect.center, 2)


class Boss2Projectile(EnemyProjectile):
    """Projectiles du Boss 2 - Violets et menacants"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((15, 15))
        self.image.fill((150, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (150, 0, int(255 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (150, 0, 255), self.rect.center, 7)
        pygame.draw.circle(surface, (200, 50, 255), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class Boss3Projectile(EnemyProjectile):
    """Projectiles du Boss 3 - Cyan/electriques"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 12

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (0, int(200 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, CYAN, self.rect.center, 6)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class HomingProjectile(EnemyProjectile):
    """Projectile a tete chercheuse pour le Boss 3"""
    def __init__(self, x, y, speed=4):
        super().__init__(x, y, 0, 1, speed)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 15
        self.lifetime = 180
        self.timer = 0
        self.turn_speed = 0.05

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(5 * progress))
            color = (255, int(100 * progress), int(100 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self, player_position=None):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Poursuite du joueur
        if player_position and self.timer < self.lifetime:
            px, py = player_position
            target_dx = px - self.rect.centerx
            target_dy = py - self.rect.centery
            dist = math.sqrt(target_dx**2 + target_dy**2)
            if dist > 0:
                target_dx /= dist
                target_dy /= dist
                self.dx += (target_dx - self.dx) * self.turn_speed
                self.dy += (target_dy - self.dy) * self.turn_speed
                d = math.sqrt(self.dx**2 + self.dy**2)
                if d > 0:
                    self.dx /= d
                    self.dy /= d

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 100, 100), self.rect.center, 5)
        pygame.draw.circle(surface, (255, 200, 200), self.rect.center, 2)


class Boss4Projectile(EnemyProjectile):
    """Projectiles du Boss 4 - Dores/solaires"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, int(180 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 215, 0), self.rect.center, 7)
        pygame.draw.circle(surface, (255, 255, 100), self.rect.center, 4)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class BouncingProjectile(EnemyProjectile):
    """Projectile qui rebondit sur les bords de l'ecran"""
    def __init__(self, x, y, dx, dy, speed=5, bounces=3):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 8
        self.bounces_left = bounces

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (255, int(100 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Rebond sur les bords
        if self.bounces_left > 0:
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.dx = -self.dx
                self.bounces_left -= 1
            if self.rect.top <= 0:
                self.dy = -self.dy
                self.bounces_left -= 1

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 100, 0), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 100), self.rect.center, 3)


class SplittingProjectile(EnemyProjectile):
    """Projectile qui se divise apres un certain temps"""
    def __init__(self, x, y, dx, dy, speed=4, split_time=40, can_split=True):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((16, 16))
        self.image.fill((200, 150, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 6
        self.timer = 0
        self.split_time = split_time
        self.can_split = can_split
        self.has_split = False

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(8 * progress)) if can_split else max(1, int(4 * progress))
            color = (200, int(150 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def should_split(self):
        return self.can_split and self.timer >= self.split_time and not self.has_split

    def split(self):
        """Retourne une liste de nouveaux projectiles"""
        self.has_split = True
        new_projectiles = []
        for angle_offset in [-45, 0, 45]:
            angle = math.atan2(self.dy, self.dx) + math.radians(angle_offset)
            ndx = math.cos(angle)
            ndy = math.sin(angle)
            new_projectiles.append(SplittingProjectile(
                self.rect.centerx, self.rect.centery,
                ndx, ndy, speed=5, can_split=False
            ))
        return new_projectiles

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            if i < len(self.trail_cache):
                trail_surf, size = self.trail_cache[i]
                surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        size = 8 if self.can_split else 5
        pygame.draw.circle(surface, (200, 150, 255), self.rect.center, size)
        pygame.draw.circle(surface, WHITE, self.rect.center, size // 2)


class Boss5Projectile(EnemyProjectile):
    """Projectiles du Boss 5 - Verts toxiques/acides"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((13, 13))
        self.image.fill((0, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 11

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (0, int(255 * progress), int(100 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (0, 255, 100), self.rect.center, 6)
        pygame.draw.circle(surface, (150, 255, 150), self.rect.center, 3)
        pygame.draw.circle(surface, WHITE, self.rect.center, 1)


class ZigZagProjectile(EnemyProjectile):
    """Projectile qui zigzague horizontalement"""
    def __init__(self, x, y, dy, speed=5, amplitude=50, frequency=0.1):
        super().__init__(x, y, 0, dy, speed)
        self.start_x = x
        self.amplitude = amplitude
        self.frequency = frequency
        self.timer = 0
        self.image = pygame.Surface((10, 10))
        self.image.fill((100, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(5 * progress))
            color = (100, int(255 * progress), 100, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.y += int(self.dy * self.speed)
        self.rect.x = self.start_x + int(math.sin(self.timer * self.frequency) * self.amplitude)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (100, 255, 100), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class GravityProjectile(EnemyProjectile):
    """Projectile affecte par la gravite"""
    def __init__(self, x, y, dx, dy, speed=8):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill((200, 100, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 12
        self.gravity = 0.15
        self.vy = dy * speed

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (200, int(100 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.vy += self.gravity
        self.rect.y += int(self.vy)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (200, 100, 255), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 255), self.rect.center, 3)


class TeleportingProjectile(EnemyProjectile):
    """Projectile qui se teleporte periodiquement"""
    def __init__(self, x, y, dx, dy, speed=4):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 5
        self.timer = 0
        self.teleport_interval = 30
        self.teleport_distance = 80

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, 0, int(255 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Teleportation
        if self.timer % self.teleport_interval == 0:
            self.rect.y += self.teleport_distance
            self.trail.clear()

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            if i < len(self.trail_cache):
                trail_surf, size = self.trail_cache[i]
                surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        # Effet de scintillement
        if (self.timer // 3) % 2 == 0:
            pygame.draw.circle(surface, (255, 0, 255), self.rect.center, 7)
        else:
            pygame.draw.circle(surface, (255, 100, 255), self.rect.center, 7)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class Boss6Projectile(EnemyProjectile):
    """Projectile du Boss 6 - noir avec aura violette"""
    def __init__(self, x, y, dx, dy, speed=5):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (50, 0, 80), (6, 6), 6)
        pygame.draw.circle(self.image, (20, 0, 40), (6, 6), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 6

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(180 * (i / len(self.trail))) if self.trail else 0
            size = max(2, int(4 * (i / max(1, len(self.trail)))))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (100, 0, 150, alpha), (size, size), size)
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))
        pygame.draw.circle(surface, (150, 0, 200), self.rect.center, 6)
        pygame.draw.circle(surface, (50, 0, 80), self.rect.center, 4)


class VortexProjectile(EnemyProjectile):
    """Projectile qui orbite autour d'un point central avant de foncer"""
    def __init__(self, x, y, target_x, target_y, speed=3):
        self.center_x = x
        self.center_y = y
        self.orbit_radius = 50
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_speed = 0.15
        self.orbit_time = 60
        self.timer = 0
        self.target_x = target_x
        self.target_y = target_y
        self.launched = False

        start_x = x + math.cos(self.orbit_angle) * self.orbit_radius
        start_y = y + math.sin(self.orbit_angle) * self.orbit_radius
        super().__init__(start_x, start_y, 0, 1, speed)

        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 180), (8, 8), 8)
        pygame.draw.circle(self.image, (200, 100, 255), (8, 8), 4)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.max_trail_length = 8
        self.trail = []

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        if not self.launched:
            self.orbit_angle += self.orbit_speed
            self.orbit_radius -= 0.3
            new_x = self.center_x + math.cos(self.orbit_angle) * max(10, self.orbit_radius)
            new_y = self.center_y + math.sin(self.orbit_angle) * max(10, self.orbit_radius)
            self.rect.center = (int(new_x), int(new_y))

            if self.timer >= self.orbit_time:
                self.launched = True
                dx = self.target_x - self.rect.centerx
                dy = self.target_y - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.dx = dx / dist
                    self.dy = dy / dist
                self.speed = 8
        else:
            self.rect.x += int(self.dx * self.speed)
            self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            progress = i / max(1, len(self.trail))
            alpha = int(200 * progress)
            size = max(2, int(6 * progress))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (150, 50, 255, alpha), (size, size), size)
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pulse = abs(math.sin(self.timer * 0.2)) * 3
        pygame.draw.circle(surface, (150, 50, 255), self.rect.center, int(8 + pulse))
        pygame.draw.circle(surface, (200, 150, 255), self.rect.center, 4)


class BlackHoleProjectile(EnemyProjectile):
    """Projectile stationnaire qui attire les projectiles du joueur"""
    def __init__(self, x, y, lifetime=180):
        super().__init__(x, y, 0, 0, 0)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = lifetime
        self.timer = 0
        self.pull_radius = 150
        self.pull_strength = 2
        self.trail = []

    def update(self):
        self.timer += 1

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, surface):
        progress = self.timer / self.lifetime
        base_alpha = int(255 * (1 - progress * 0.5))

        for i in range(3):
            ring_size = 20 - i * 5 + int(5 * abs(math.sin(self.timer * 0.1 + i)))
            ring_alpha = max(0, base_alpha - i * 50)
            ring_surf = pygame.Surface((ring_size*2 + 10, ring_size*2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (100, 0, 150, ring_alpha),
                             (ring_size + 5, ring_size + 5), ring_size, 2)
            surface.blit(ring_surf, (self.rect.centerx - ring_size - 5,
                                     self.rect.centery - ring_size - 5))

        pygame.draw.circle(surface, (20, 0, 30), self.rect.center, 12)
        pygame.draw.circle(surface, (0, 0, 0), self.rect.center, 8)


class MirrorProjectile(EnemyProjectile):
    """Projectile qui se duplique quand il atteint certaines positions"""
    def __init__(self, x, y, dx, dy, speed=4, can_split=True):
        super().__init__(x, y, dx, dy, speed)
        self.can_split = can_split
        self.split_y = y + 200
        self.has_split = False
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (180, 0, 255), [(5, 0), (10, 10), (0, 10)])
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 5
        self.children = []

    def update(self):
        super().update()
        if self.can_split and not self.has_split and self.rect.centery >= self.split_y:
            self.has_split = True

    def should_split(self):
        return self.can_split and self.has_split and not self.children

    def split(self):
        """Cree deux copies allant dans des directions opposees"""
        self.children = [
            MirrorProjectile(self.rect.centerx, self.rect.centery,
                           self.dx - 0.5, self.dy, self.speed, can_split=False),
            MirrorProjectile(self.rect.centerx, self.rect.centery,
                           self.dx + 0.5, self.dy, self.speed, can_split=False)
        ]
        return self.children


class PulseWaveProjectile(EnemyProjectile):
    """Onde de choc circulaire qui s'etend"""
    def __init__(self, x, y, speed=3):
        super().__init__(x, y, 0, 0, speed)
        self.radius = 10
        self.max_radius = 300
        self.thickness = 8
        self.center = (x, y)
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.trail = []

    def update(self):
        self.radius += self.speed
        self.rect = pygame.Rect(
            self.center[0] - self.radius,
            self.center[1] - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def is_expired(self):
        return self.radius >= self.max_radius

    def check_collision(self, other_rect):
        """Collision speciale pour l'anneau"""
        dx = other_rect.centerx - self.center[0]
        dy = other_rect.centery - self.center[1]
        dist = math.sqrt(dx*dx + dy*dy)
        return abs(dist - self.radius) < self.thickness + 10

    def draw(self, surface):
        alpha = int(255 * (1 - self.radius / self.max_radius))
        wave_surf = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(wave_surf, (150, 0, 200, alpha),
                          (self.radius + 10, self.radius + 10), int(self.radius), self.thickness)
        surface.blit(wave_surf, (self.center[0] - self.radius - 10,
                                  self.center[1] - self.radius - 10))
