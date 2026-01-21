import pygame
import math
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, RED, YELLOW, ORANGE, CYAN, WHITE


class TrailedProjectile:
    """Classe de base pour tous les projectiles avec traînée"""
    def __init__(self, max_trail_length, trail_color_func, trail_size_func):
        self.trail = []
        self.max_trail_length = max_trail_length
        self.trail_cache = []

        for i in range(max_trail_length):
            progress = i / max_trail_length if max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = trail_size_func(progress)
            color = trail_color_func(progress, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update_trail(self):
        """Met à jour la traînée avec la position actuelle"""
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw_trail(self, surface):
        """Dessine la traînée sur la surface"""
        for i, pos in enumerate(self.trail):
            if i < len(self.trail_cache):
                trail_surf, size = self.trail_cache[i]
                surface.blit(trail_surf, (pos[0] - size, pos[1] - size))


class Projectile(TrailedProjectile):
    def __init__(self, x, y, speed=10):
        super().__init__(
            max_trail_length=6,
            trail_color_func=lambda progress, alpha: (int(200 + 55 * progress), 255, 0, alpha),
            trail_size_func=lambda progress: max(1, int(4 * progress))
        )
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.y -= self.speed

    def draw(self, surface):
        self.draw_trail(surface)
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
        self.update_trail()
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
        self.update_trail()
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


class EnemyProjectile(TrailedProjectile):
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(
            max_trail_length=5,
            trail_color_func=lambda progress, alpha: (RED[0], RED[1], RED[2], alpha),
            trail_size_func=lambda progress: max(1, int(3 * progress))
        )
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        surface.blit(self.image, self.rect)


class BossProjectile(EnemyProjectile):
    """Projectiles du Boss - Plus gros et plus visibles"""
    def __init__(self, x, y, dx, dy, speed=7):
        # Initialiser la classe de base TrailedProjectile directement
        TrailedProjectile.__init__(
            self,
            max_trail_length=8,
            trail_color_func=lambda progress, alpha: (255, int(100 + 65 * progress), 0, alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )
        self.image = pygame.Surface((15, 15))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, ORANGE, self.rect.center, 7)
        pygame.draw.circle(surface, RED, self.rect.center, 5)
        pygame.draw.circle(surface, YELLOW, self.rect.center, 2)


class Boss2Projectile(EnemyProjectile):
    """Projectiles du Boss 2 - Violets et menacants"""
    def __init__(self, x, y, dx, dy, speed=7):
        TrailedProjectile.__init__(
            self,
            max_trail_length=10,
            trail_color_func=lambda progress, alpha: (150, 0, int(255 * progress), alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )
        self.image = pygame.Surface((15, 15))
        self.image.fill((150, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (150, 0, 255), self.rect.center, 7)
        pygame.draw.circle(surface, (200, 50, 255), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class Boss3Projectile(EnemyProjectile):
    """Projectiles du Boss 3 - Cyan/electriques"""
    def __init__(self, x, y, dx, dy, speed=7):
        TrailedProjectile.__init__(
            self,
            max_trail_length=12,
            trail_color_func=lambda progress, alpha: (0, int(200 * progress), 255, alpha),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )
        self.image = pygame.Surface((12, 12))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, CYAN, self.rect.center, 6)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class HomingProjectile(EnemyProjectile):
    """Projectile a tete chercheuse pour le Boss 3"""
    def __init__(self, x, y, speed=4):
        TrailedProjectile.__init__(
            self,
            max_trail_length=15,
            trail_color_func=lambda progress, alpha: (255, int(100 * progress), int(100 * progress), alpha),
            trail_size_func=lambda progress: max(2, int(5 * progress))
        )
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = 0
        self.dy = 1
        self.speed = speed
        self.homing_duration = 180
        self.timer = 0
        self.turn_speed = 0.05
        self.launched = False
        self.super_speed = 15

    def update(self, player_position=None):
        self.timer += 1
        self.update_trail()

        # Poursuite du joueur
        if player_position and self.timer < self.homing_duration:
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
        else:
            # Apres la phase de guidage, fonce tout droit a supervitesse
            if not self.launched:
                self.launched = True
                # Normaliser la direction actuelle
                d = math.sqrt(self.dx**2 + self.dy**2)
                if d > 0:
                    self.dx /= d
                    self.dy /= d
            self.rect.x += int(self.dx * self.super_speed)
            self.rect.y += int(self.dy * self.super_speed)

    def is_expired(self):
        # Le missile expire seulement quand il sort de l'ecran
        return (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (255, 100, 100), self.rect.center, 5)
        pygame.draw.circle(surface, (255, 200, 200), self.rect.center, 2)


class Boss4Projectile(EnemyProjectile):
    """Projectiles du Boss 4 - Dores/solaires"""
    def __init__(self, x, y, dx, dy, speed=7):
        TrailedProjectile.__init__(
            self,
            max_trail_length=10,
            trail_color_func=lambda progress, alpha: (255, int(180 * progress), 0, alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (255, 215, 0), self.rect.center, 7)
        pygame.draw.circle(surface, (255, 255, 100), self.rect.center, 4)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class BouncingProjectile(EnemyProjectile):
    """Projectile qui rebondit sur les bords de l'ecran"""
    def __init__(self, x, y, dx, dy, speed=5, bounces=3):
        TrailedProjectile.__init__(
            self,
            max_trail_length=8,
            trail_color_func=lambda progress, alpha: (255, int(100 * progress), 0, alpha),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.bounces_left = bounces

    def update(self):
        self.update_trail()
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
        self.draw_trail(surface)
        pygame.draw.circle(surface, (255, 100, 0), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 100), self.rect.center, 3)


class SplittingProjectile(EnemyProjectile):
    """Projectile qui se divise apres un certain temps"""
    def __init__(self, x, y, dx, dy, speed=4, split_time=40, can_split=True):
        TrailedProjectile.__init__(
            self,
            max_trail_length=6,
            trail_color_func=lambda progress, alpha: (200, int(150 * progress), 255, alpha),
            trail_size_func=lambda progress: max(2, int(8 * progress)) if can_split else max(1, int(4 * progress))
        )
        self.image = pygame.Surface((16, 16))
        self.image.fill((200, 150, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.timer = 0
        self.split_time = split_time
        self.can_split = can_split
        self.has_split = False

    def update(self):
        self.timer += 1
        self.update_trail()
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
        TrailedProjectile.__init__(
            self,
            max_trail_length=11,
            trail_color_func=lambda progress, alpha: (0, int(255 * progress), int(100 * progress), alpha),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )
        self.image = pygame.Surface((13, 13))
        self.image.fill((0, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (0, 255, 100), self.rect.center, 6)
        pygame.draw.circle(surface, (150, 255, 150), self.rect.center, 3)
        pygame.draw.circle(surface, WHITE, self.rect.center, 1)


class ZigZagProjectile(EnemyProjectile):
    """Projectile qui zigzague horizontalement"""
    def __init__(self, x, y, dy, speed=5, amplitude=50, frequency=0.1):
        TrailedProjectile.__init__(
            self,
            max_trail_length=10,
            trail_color_func=lambda progress, alpha: (100, int(255 * progress), 100, alpha),
            trail_size_func=lambda progress: max(2, int(5 * progress))
        )
        self.image = pygame.Surface((10, 10))
        self.image.fill((100, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = 0
        self.dy = dy
        self.speed = speed
        self.start_x = x
        self.amplitude = amplitude
        self.frequency = frequency
        self.timer = 0

    def update(self):
        self.timer += 1
        self.update_trail()
        self.rect.y += int(self.dy * self.speed)
        self.rect.x = self.start_x + int(math.sin(self.timer * self.frequency) * self.amplitude)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (100, 255, 100), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class GravityProjectile(EnemyProjectile):
    """Projectile affecte par la gravite"""
    def __init__(self, x, y, dx, dy, speed=8):
        TrailedProjectile.__init__(
            self,
            max_trail_length=12,
            trail_color_func=lambda progress, alpha: (200, int(100 * progress), 255, alpha),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )
        self.image = pygame.Surface((12, 12))
        self.image.fill((200, 100, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.gravity = 0.15
        self.vy = dy * speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.vy += self.gravity
        self.rect.y += int(self.vy)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (200, 100, 255), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 255), self.rect.center, 3)


class TeleportingProjectile(EnemyProjectile):
    """Projectile qui se teleporte periodiquement"""
    def __init__(self, x, y, dx, dy, speed=4):
        TrailedProjectile.__init__(
            self,
            max_trail_length=5,
            trail_color_func=lambda progress, alpha: (255, 0, int(255 * progress), alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.timer = 0
        self.teleport_interval = 30
        self.teleport_distance = 80

    def update(self):
        self.timer += 1
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Teleportation
        if self.timer % self.teleport_interval == 0:
            self.rect.y += self.teleport_distance
            self.trail.clear()

    def draw(self, surface):
        self.draw_trail(surface)
        # Effet de scintillement
        if (self.timer // 3) % 2 == 0:
            pygame.draw.circle(surface, (255, 0, 255), self.rect.center, 7)
        else:
            pygame.draw.circle(surface, (255, 100, 255), self.rect.center, 7)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class Boss6Projectile(EnemyProjectile):
    """Projectile du Boss 6 - noir avec aura violette"""
    def __init__(self, x, y, dx, dy, speed=5):
        TrailedProjectile.__init__(
            self,
            max_trail_length=6,
            trail_color_func=lambda progress, alpha: (100, 0, 150, int(180 * progress)),
            trail_size_func=lambda progress: max(2, int(4 * progress))
        )
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (50, 0, 80), (6, 6), 6)
        pygame.draw.circle(self.image, (20, 0, 40), (6, 6), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
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

        TrailedProjectile.__init__(
            self,
            max_trail_length=8,
            trail_color_func=lambda progress, alpha: (150, 50, 255, int(200 * progress)),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )

        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 180), (8, 8), 8)
        pygame.draw.circle(self.image, (200, 100, 255), (8, 8), 4)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.dx = 0
        self.dy = 1
        self.speed = speed

    def update(self):
        self.timer += 1
        self.update_trail()

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
        self.draw_trail(surface)
        pulse = abs(math.sin(self.timer * 0.2)) * 3
        pygame.draw.circle(surface, (150, 50, 255), self.rect.center, int(8 + pulse))
        pygame.draw.circle(surface, (200, 150, 255), self.rect.center, 4)


class BlackHoleProjectile(EnemyProjectile):
    """Projectile stationnaire qui attire les projectiles du joueur"""
    def __init__(self, x, y, lifetime=180):
        TrailedProjectile.__init__(
            self,
            max_trail_length=0,
            trail_color_func=lambda progress, alpha: (0, 0, 0, 0),
            trail_size_func=lambda progress: 0
        )
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = 0
        self.dy = 0
        self.speed = 0
        self.lifetime = lifetime
        self.timer = 0
        self.pull_radius = 150
        self.pull_strength = 2

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
        TrailedProjectile.__init__(
            self,
            max_trail_length=5,
            trail_color_func=lambda progress, alpha: (180, 0, 255, alpha),
            trail_size_func=lambda progress: max(1, int(3 * progress))
        )
        self.can_split = can_split
        self.split_y = y + 200
        self.has_split = False
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (180, 0, 255), [(5, 0), (10, 10), (0, 10)])
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.children = []

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)
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
        TrailedProjectile.__init__(
            self,
            max_trail_length=0,
            trail_color_func=lambda progress, alpha: (0, 0, 0, 0),
            trail_size_func=lambda progress: 0
        )
        self.radius = 10
        self.max_radius = 300
        self.thickness = 8
        self.center = (x, y)
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = 0
        self.dy = 0
        self.speed = speed

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


class Boss7Projectile(EnemyProjectile):
    """Projectile du Boss 7 - gris neutre"""
    def __init__(self, x, y, dx, dy, speed=6):
        TrailedProjectile.__init__(
            self,
            max_trail_length=8,
            trail_color_func=lambda progress, alpha: (180, 180, 180, alpha),
            trail_size_func=lambda progress: max(2, int(6 * progress))
        )
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 180, 180), (7, 7), 7)
        pygame.draw.circle(self.image, (220, 220, 220), (7, 7), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.update_trail()
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)
        pygame.draw.circle(surface, (180, 180, 180), self.rect.center, 7)
        pygame.draw.circle(surface, (220, 220, 220), self.rect.center, 4)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class BallBreakerProjectile(EnemyProjectile):
    """
    Projectile special du Boss 7 - Ball Breaker
    Lance en ligne droite vers le joueur, peut rebondir jusqu'a 4 fois.
    Rebondit sur les bords de l'ecran et sur les autres balles.
    Au 5eme rebond: traverse les bords ou explose si c'est une balle.
    """
    def __init__(self, x, y, target_x, target_y, speed=8):
        # Calculer direction initiale vers le joueur
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist

        TrailedProjectile.__init__(
            self,
            max_trail_length=12,
            trail_color_func=lambda progress, alpha: (255, 100, 150, alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )

        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 150), (24, 24), 24)
        pygame.draw.circle(self.image, (255, 150, 200), (24, 24), 15)
        pygame.draw.circle(self.image, WHITE, (24, 24), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.bounces_left = 4
        self.margin = 10
        self.ball_radius = 24

    def update(self, other_projectiles=None):
        self.update_trail()

        # Déplacement
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Collision avec d'autres balles (EdgeRoller ou BallBreaker) - vérifier AVANT les bords
        ball_collision = False
        if other_projectiles and self.bounces_left > 0:
            for other in other_projectiles:
                if other is self:
                    continue
                if isinstance(other, (EdgeRollerProjectile, BallBreakerProjectile)):
                    # Calcul de la distance entre les centres
                    dx_ball = self.rect.centerx - other.rect.centerx
                    dy_ball = self.rect.centery - other.rect.centery
                    distance = math.sqrt(dx_ball*dx_ball + dy_ball*dy_ball)
                    # Collision si distance < somme des rayons (24 + 24 = 48)
                    if distance < 48 and distance > 0:
                        # Normaliser le vecteur de collision
                        dx_ball /= distance
                        dy_ball /= distance

                        # Réfléchir la direction selon la normale de collision
                        # Formule de réflexion: v' = v - 2(v·n)n
                        dot = self.dx * dx_ball + self.dy * dy_ball
                        self.dx = self.dx - 2 * dot * dx_ball
                        self.dy = self.dy - 2 * dot * dy_ball

                        # Repousser les balles pour éviter qu'elles restent collées
                        overlap = 48 - distance
                        self.rect.x += int(dx_ball * (overlap + 2))
                        self.rect.y += int(dy_ball * (overlap + 2))

                        self.bounces_left -= 1
                        ball_collision = True
                        break

        # Rebond sur les bords si des rebonds restent (seulement si pas de collision avec une balle)
        if self.bounces_left > 0 and not ball_collision:
            bounced_this_frame = False
            # Rebond gauche/droite
            if self.rect.left <= self.margin:
                self.rect.left = self.margin
                self.dx = abs(self.dx)
                if not bounced_this_frame:
                    self.bounces_left -= 1
                    bounced_this_frame = True
            elif self.rect.right >= SCREEN_WIDTH - self.margin:
                self.rect.right = SCREEN_WIDTH - self.margin
                self.dx = -abs(self.dx)
                if not bounced_this_frame:
                    self.bounces_left -= 1
                    bounced_this_frame = True

            # Rebond haut/bas
            if self.rect.top <= self.margin:
                self.rect.top = self.margin
                self.dy = abs(self.dy)
                if not bounced_this_frame:
                    self.bounces_left -= 1
                    bounced_this_frame = True
            elif self.rect.bottom >= SCREEN_HEIGHT - self.margin:
                self.rect.bottom = SCREEN_HEIGHT - self.margin
                self.dy = -abs(self.dy)
                if not bounced_this_frame:
                    self.bounces_left -= 1
                    bounced_this_frame = True

    def should_explode(self):
        """Retourne True si le projectile doit exploser (5ème rebond sur une balle)"""
        # Cette méthode sera appelée par le code de gestion des projectiles
        return self.bounces_left < 0

    def draw(self, surface):
        self.draw_trail(surface)

        # Couleur varie selon le nombre de rebonds restants
        if self.bounces_left >= 3:
            color1, color2 = (255, 100, 150), (255, 150, 200)
        elif self.bounces_left >= 2:
            color1, color2 = (255, 150, 100), (255, 200, 150)
        elif self.bounces_left >= 1:
            color1, color2 = (255, 200, 100), (255, 230, 150)
        else:
            color1, color2 = (255, 100, 100), (255, 150, 150)

        pygame.draw.circle(surface, color1, self.rect.center, 24)
        pygame.draw.circle(surface, color2, self.rect.center, 15)
        pygame.draw.circle(surface, WHITE, self.rect.center, 6)


class EdgeRollerProjectile(EnemyProjectile):
    """
    Projectile special du Boss 7 - Edge Roller
    Comportement en plusieurs phases:
    1. Fonce vers le joueur
    2. Quand il touche un bord, longe le contour de l'ecran
    3. Quand il remonte et est aligne horizontalement avec le joueur, fait un arc pour orbiter
    4. Apres 1 seconde, fonce vers le joueur et quitte l'ecran
    """
    # Phases du projectile
    PHASE_CHASE = 0       # Fonce vers le joueur
    PHASE_ROLL = 1        # Longe les bords
    PHASE_ORBIT = 2       # Orbite autour du joueur
    PHASE_FINAL = 3       # Fonce vers le joueur pour de bon

    # Directions de roulement
    ROLL_DOWN = 0   # Descend
    ROLL_RIGHT = 1  # Va a droite
    ROLL_UP = 2     # Remonte
    ROLL_LEFT = 3   # Va a gauche

    def __init__(self, x, y, target_x, target_y, speed=7):
        # Calculer direction initiale vers le joueur
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist

        TrailedProjectile.__init__(
            self,
            max_trail_length=12,
            trail_color_func=lambda progress, alpha: (100, 200, 255, alpha),
            trail_size_func=lambda progress: max(2, int(7 * progress))
        )

        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 200, 255), (24, 24), 24)
        pygame.draw.circle(self.image, (150, 230, 255), (24, 24), 15)
        pygame.draw.circle(self.image, WHITE, (24, 24), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.base_speed = speed
        self.speed = speed  # Sera modifié dynamiquement
        self.max_speed = speed * 3  # Vitesse maximale

        self.phase = self.PHASE_CHASE
        self.roll_direction = None
        self.roll_speed = speed  # Sera modifié dynamiquement
        self.margin = 10  # Marge par rapport aux bords
        self.clockwise = True  # Sens de rotation (True = horaire, False = anti-horaire)

        # Timer global pour la courbe de vitesse parabolique
        self.global_timer = 0

        # Pour la phase orbit
        self.orbit_timer = 0
        self.orbit_duration = 60  # 1 seconde a 60 FPS
        self.orbit_phase_1_duration = 20  # Duree de l'acceleration (phase 1)
        self.orbit_phase_2_duration = 20  # Duree a vitesse max (phase 2)
        # Phase 3 = reste du temps (orbit_duration - phase_1 - phase_2)
        self.orbit_center_x = 0
        self.orbit_center_y = 0
        self.orbit_radius = 0
        self.orbit_angle = 0
        self.orbit_direction = 1  # 1 = sens horaire, -1 = anti-horaire

        # Pour la phase finale
        self.final_timer = 0
        self.final_wait = 60  # 1 seconde d'attente avant de foncer
        self.target_x = target_x
        self.target_y = target_y

        # Memorise si on a passe par le bas de l'ecran
        self.passed_bottom = False

    def update(self, player_position=None, other_projectiles=None):
        self.update_trail()

        if player_position:
            self.target_x, self.target_y = player_position

        # Mettre à jour la vitesse selon la courbe parabolique
        self._update_speed()

        if self.phase == self.PHASE_CHASE:
            self._update_chase()
        elif self.phase == self.PHASE_ROLL:
            self._update_roll()
        elif self.phase == self.PHASE_ORBIT:
            self._update_orbit()
        elif self.phase == self.PHASE_FINAL:
            self._update_final()

    def _update_speed(self):
        """Met à jour la vitesse selon une courbe parabolique sur les phases 1, 2 et 3"""
        if self.phase == self.PHASE_FINAL:
            return  # Phase finale utilise sa propre vitesse

        self.global_timer += 1

        # Phase 1 (CHASE): Accélération exponentielle sur 1 seconde
        if self.phase == self.PHASE_CHASE:
            # Accélération exponentielle: commence lent, monte vers max_speed
            # On utilise une formule qui monte rapidement au début puis ralentit
            progress = min(1.0, self.global_timer / 60.0)  # Sur 1 seconde (60 frames)
            speed_factor = 1.0 - math.exp(-progress * 4.0)  # Accélération exponentielle
            self.speed = self.base_speed + (self.max_speed - self.base_speed) * speed_factor
            self.roll_speed = self.speed

        # Phase 2 (ROLL): Continue d'accélérer si pas encore au max, sinon reste au max
        elif self.phase == self.PHASE_ROLL:
            # Continuer l'accélération ou rester au max
            if self.speed < self.max_speed:
                progress = min(1.0, self.global_timer / 120.0)  # Sur ~2 secondes au total
                speed_factor = 1.0 - math.exp(-progress * 4.0)
                self.speed = self.base_speed + (self.max_speed - self.base_speed) * speed_factor
            else:
                self.speed = self.max_speed
            self.roll_speed = self.speed

        # Phase 3 (ORBIT): Décélération linéaire sur 1 seconde
        elif self.phase == self.PHASE_ORBIT:
            # Décélération linéaire: 100% -> 0%
            decay_progress = self.orbit_timer / self.orbit_duration  # 0 à 1 sur 60 frames
            speed_factor = 1.0 - decay_progress  # Décroissance linéaire de 1 à 0
            self.speed = self.max_speed * speed_factor

    def _update_chase(self):
        """Phase 1: Fonce vers le joueur jusqu'a toucher un bord"""
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Verifier si on touche un bord et determiner le sens de rotation
        if self.rect.left <= self.margin:
            self.rect.left = self.margin
            self.clockwise = False  # Touche le bord gauche -> sens anti-horaire
            self._start_rolling(self.ROLL_DOWN)
        elif self.rect.right >= SCREEN_WIDTH - self.margin:
            self.rect.right = SCREEN_WIDTH - self.margin
            self.clockwise = True  # Touche le bord droit -> sens horaire
            self._start_rolling(self.ROLL_DOWN)
        elif self.rect.top <= self.margin:
            self.rect.top = self.margin
            # Determiner le sens selon si on est plutot a gauche ou a droite
            if self.rect.centerx < SCREEN_WIDTH / 2:
                # Cote gauche du haut -> sens anti-horaire -> va vers la droite
                self.clockwise = False
                self._start_rolling(self.ROLL_RIGHT)
            else:
                # Cote droit du haut -> sens horaire -> va vers la gauche
                self.clockwise = True
                self._start_rolling(self.ROLL_LEFT)
        elif self.rect.bottom >= SCREEN_HEIGHT - self.margin:
            self.rect.bottom = SCREEN_HEIGHT - self.margin
            self.passed_bottom = True  # Deja au bas
            # Determiner le sens selon si on est plutot a gauche ou a droite
            if self.rect.centerx < SCREEN_WIDTH / 2:
                # Cote gauche du bas -> va vers la GAUCHE, puis remontera sur le bord GAUCHE
                # On inverse clockwise car pour remonter sur le bord gauche, il faut clockwise=True
                self.clockwise = True
                self._start_rolling(self.ROLL_LEFT)
            else:
                # Cote droit du bas -> va vers la DROITE, puis remontera sur le bord DROIT
                # On inverse clockwise car pour remonter sur le bord droit, il faut clockwise=False
                self.clockwise = False
                self._start_rolling(self.ROLL_RIGHT)

    def _start_rolling(self, direction):
        """Commence a longer le bord"""
        self.phase = self.PHASE_ROLL
        self.roll_direction = direction

    def _update_roll(self):
        """Phase 2: Longe les bords de l'ecran"""
        if self.roll_direction == self.ROLL_DOWN:
            # Descend sur un bord vertical
            self.rect.y += self.roll_speed
            if self.clockwise:
                # clockwise = True : bord droit -> bas -> gauche -> haut -> droit
                self.rect.right = SCREEN_WIDTH - self.margin
                if self.rect.bottom >= SCREEN_HEIGHT - self.margin:
                    self.rect.bottom = SCREEN_HEIGHT - self.margin
                    self.roll_direction = self.ROLL_LEFT
                    self.passed_bottom = True
            else:
                # clockwise = False : bord gauche -> bas -> droite -> haut -> gauche
                self.rect.left = self.margin
                if self.rect.bottom >= SCREEN_HEIGHT - self.margin:
                    self.rect.bottom = SCREEN_HEIGHT - self.margin
                    self.roll_direction = self.ROLL_RIGHT
                    self.passed_bottom = True

        elif self.roll_direction == self.ROLL_RIGHT:
            # Va a droite sur un bord horizontal
            self.rect.x += self.roll_speed
            if self.clockwise:
                # Va a droite sur le bord bas (sens horaire: touche bas droit->va droite sur le bas)
                self.rect.bottom = SCREEN_HEIGHT - self.margin
                self.passed_bottom = True
                if self.rect.right >= SCREEN_WIDTH - self.margin:
                    self.rect.right = SCREEN_WIDTH - self.margin
                    self.roll_direction = self.ROLL_UP
            else:
                # Va a droite sur le bord bas aussi (dans le sens anti-horaire: gauche->bas->droit)
                self.rect.bottom = SCREEN_HEIGHT - self.margin
                self.passed_bottom = True
                if self.rect.right >= SCREEN_WIDTH - self.margin:
                    self.rect.right = SCREEN_WIDTH - self.margin
                    self.roll_direction = self.ROLL_UP

        elif self.roll_direction == self.ROLL_UP:
            # Remonte sur un bord vertical
            self.rect.y -= self.roll_speed
            if self.clockwise:
                # Remonte sur le bord gauche (sens horaire: droit->bas->ROLL_LEFT->coin bas-gauche->remonte bord gauche)
                self.rect.left = self.margin

                # Verifier si on est au niveau du joueur (axe Y) et qu'on a fait le tour
                if self.passed_bottom and self.rect.centery <= self.target_y:
                    self._start_orbit()

                # Si on atteint le haut sans avoir croise le joueur, continuer le tour
                if self.rect.top <= self.margin:
                    self.rect.top = self.margin
                    self.roll_direction = self.ROLL_RIGHT
            else:
                # Remonte sur le bord droit (sens anti-horaire: gauche->bas->ROLL_RIGHT->coin bas-droit->remonte bord droit)
                self.rect.right = SCREEN_WIDTH - self.margin

                # Verifier si on est au niveau du joueur (axe Y) et qu'on a fait le tour
                if self.passed_bottom and self.rect.centery <= self.target_y:
                    self._start_orbit()

                # Si on atteint le haut sans avoir croise le joueur, continuer le tour
                if self.rect.top <= self.margin:
                    self.rect.top = self.margin
                    self.roll_direction = self.ROLL_LEFT

        elif self.roll_direction == self.ROLL_LEFT:
            # Va a gauche sur un bord horizontal
            self.rect.x -= self.roll_speed
            if self.clockwise:
                # Va a gauche sur le bord bas (sens horaire: droit->bas->gauche)
                self.rect.bottom = SCREEN_HEIGHT - self.margin
                self.passed_bottom = True
                if self.rect.left <= self.margin:
                    self.rect.left = self.margin
                    self.roll_direction = self.ROLL_UP
            else:
                # Va a gauche sur le bord bas aussi (sens anti-horaire: touche bas gauche->va gauche sur le bas)
                self.rect.bottom = SCREEN_HEIGHT - self.margin
                self.passed_bottom = True
                if self.rect.left <= self.margin:
                    self.rect.left = self.margin
                    self.roll_direction = self.ROLL_UP

    def _start_orbit(self):
        """Commence l'orbite autour du joueur"""
        self.phase = self.PHASE_ORBIT
        self.orbit_timer = 0

        # Centre de l'orbite = position du joueur
        self.orbit_center_x = self.target_x
        self.orbit_center_y = self.target_y

        # Rayon = distance actuelle au joueur
        dx = self.rect.centerx - self.orbit_center_x
        dy = self.rect.centery - self.orbit_center_y
        self.orbit_radius = math.sqrt(dx*dx + dy*dy)

        # Angle initial
        self.orbit_angle = math.atan2(dy, dx)

        # Direction d'orbite depend du cote : bord droit = anti-horaire (-1), bord gauche = horaire (1)
        if self.rect.centerx > SCREEN_WIDTH / 2:
            # Sur le bord droit -> orbite anti-horaire pour aller vers la gauche
            self.orbit_direction = -1
        else:
            # Sur le bord gauche -> orbite horaire pour aller vers la droite
            self.orbit_direction = 1
        self.orbit_speed_angle = 0.027  # Vitesse ralentie (divisée par 3)

    def _update_orbit(self):
        """Phase 3: Orbite autour du joueur pour quitter le contour
        La vitesse est gérée par _update_speed() et décélère exponentiellement
        """
        self.orbit_timer += 1

        # La vitesse angulaire est proportionnelle à la vitesse linéaire
        # qui est maintenant gérée par _update_speed()
        speed_ratio = self.speed / self.max_speed if self.max_speed > 0 else 0
        current_speed = self.orbit_speed_angle * speed_ratio

        # Faire l'orbite avec la vitesse calculee
        self.orbit_angle += current_speed * self.orbit_direction

        # Reduire le rayon progressivement pour une trajectoire en spirale sortante
        self.orbit_radius -= 1.5

        new_x = self.orbit_center_x + math.cos(self.orbit_angle) * self.orbit_radius
        new_y = self.orbit_center_y + math.sin(self.orbit_angle) * self.orbit_radius
        self.rect.center = (int(new_x), int(new_y))

        # Apres un quart de tour ou si le rayon devient petit, passer a la phase finale
        if self.orbit_timer >= self.orbit_duration or self.orbit_radius < 50:
            self.phase = self.PHASE_FINAL
            self.final_timer = 0

    def _update_final(self):
        """Phase 4: Fonce directement vers le joueur sans attendre"""
        self.final_timer += 1

        if self.final_timer == 1:
            # Premier frame: calculer la direction et augmenter la vitesse
            dx = self.target_x - self.rect.centerx
            dy = self.target_y - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.dx = dx / dist
                self.dy = dy / dist
            # Vitesse x2 pour la phase finale
            self.speed = self.base_speed * 2

        # Continuer en ligne droite avec la direction calculee
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        self.draw_trail(surface)

        # Couleur varie selon la phase
        if self.phase == self.PHASE_CHASE:
            color1, color2 = (100, 200, 255), (150, 230, 255)
        elif self.phase == self.PHASE_ROLL:
            color1, color2 = (100, 255, 200), (150, 255, 230)
        elif self.phase == self.PHASE_ORBIT:
            color1, color2 = (255, 200, 100), (255, 230, 150)
        else:  # PHASE_FINAL
            color1, color2 = (255, 100, 100), (255, 150, 150)

        pygame.draw.circle(surface, color1, self.rect.center, 24)
        pygame.draw.circle(surface, color2, self.rect.center, 15)
        pygame.draw.circle(surface, WHITE, self.rect.center, 6)
