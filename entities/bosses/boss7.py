import pygame
import random
import math

from config import SCREEN_WIDTH
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss7Projectile, EdgeRollerProjectile, BallBreakerProjectile, CurveStalkerProjectile, PathChaserProjectile, PathWanderProjectile, FieldDodgerProjectile


class Boss7(Enemy):
    """Septieme Boss - Le Maitre des Spheres aux effets multiples"""
    def __init__(self, x, y, speed=2, target_y=100):
        self.size = 180
        self.hp = 80
        self.max_hp = 80
        self.speed = speed
        self.target_y = target_y
        self.timer = 0
        self.pattern_index = 0         # Pattern actuel
        self.pattern_cooldown = 60     # Délai initial avant le premier tir (1s)
        self.is_dying = False
        self.death_timer = 0
        self.death_explosions = []

        # Mouvement
        self.movement_angle = 0
        self.movement_amplitude = 40

        # Sprite placeholder gris
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.create_sprite()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # Animation
        self.pulse_timer = 0

    def create_sprite(self):
        """Cree un sprite placeholder gris pour le Boss 7"""
        center = self.size // 2

        # Fond gris avec degradé
        for r in range(center, 0, -2):
            progress = r / center
            gray = int(80 + 60 * progress)
            alpha = int(220 * progress)
            pygame.draw.circle(self.base_image, (gray, gray, gray, alpha),
                             (center, center), r)

        # Contour
        pygame.draw.circle(self.base_image, (150, 150, 150), (center, center), center - 5, 3)

        # Noyau central
        pygame.draw.circle(self.base_image, (100, 100, 100), (center, center), 30)
        pygame.draw.circle(self.base_image, (130, 130, 130), (center, center), 20)
        pygame.draw.circle(self.base_image, (180, 180, 180), (center, center), 10)

        # Indicateurs de spheres (petits cercles autour)
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            orb_x = center + int(math.cos(angle) * 60)
            orb_y = center + int(math.sin(angle) * 60)
            pygame.draw.circle(self.base_image, (120, 200, 255), (orb_x, orb_y), 12)
            pygame.draw.circle(self.base_image, (180, 230, 255), (orb_x, orb_y), 7)

    def take_damage(self, damage):
        self.hp -= damage

    def update(self, player_pos, projectiles_list):
        if self.is_dying:
            return self.update_death()

        self.timer += 1
        self.pulse_timer += 1
        self.movement_angle += 0.02

        # Mouvement d'entree
        if self.rect.centery < self.target_y:
            self.rect.y += self.speed
        else:
            # Mouvement lateral fluide
            offset_x = math.sin(self.movement_angle) * self.movement_amplitude
            offset_y = math.cos(self.movement_angle * 0.7) * (self.movement_amplitude * 0.3)
            base_x = SCREEN_WIDTH // 2 + offset_x

            self.rect.centerx = int(base_x)
            self.rect.centery = int(self.target_y + offset_y)

            # Gestion des patterns
            if self.pattern_cooldown > 0:
                self.pattern_cooldown -= 1
            else:
                self.execute_pattern(player_pos, projectiles_list)

        return False

    def execute_pattern(self, player_pos, projectiles_list):
        """Exécute le pattern actuel et enclenche le cooldown."""
        if self.pattern_index == 0:
            self.pattern_ball_breaker_diagonal(projectiles_list)
            self.pattern_cooldown = 300  # 5 secondes (60 * 5)

    def pattern_ball_breaker_diagonal(self, projectiles_list):
        """Pattern 1 : tire Ball Breaker dans les deux diagonales basses (210° et 330°)."""
        cx, cy = self.rect.center
        for angle_deg, offset_x in [(210, -50), (330, 50)]:
            angle_rad = math.radians(angle_deg)
            spawn_x = cx + offset_x
            # Convertit l'angle standard (y vers le haut) en coordonnées écran (y vers le bas)
            target_x = spawn_x + math.cos(angle_rad) * 1000
            target_y = cy - math.sin(angle_rad) * 1000
            proj = BallBreakerProjectile(spawn_x, cy, target_x, target_y, speed=8)
            projectiles_list.append(proj)

    def update_death(self):
        self.death_timer += 1

        if self.death_timer % 8 == 0:
            offset_x = random.randint(-self.size//2, self.size//2)
            offset_y = random.randint(-self.size//2, self.size//2)
            exp = Explosion(self.rect.centerx + offset_x,
                          self.rect.centery + offset_y,
                          duration=600)
            self.death_explosions.append(exp)

        for exp in self.death_explosions:
            exp.update()
        self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

        if self.death_timer < 120:
            shrink = 1 - (self.death_timer / 120) * 0.5
            self.image = pygame.transform.rotozoom(self.base_image,
                                                    self.death_timer * 3,
                                                    shrink)
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.death_timer >= 150:
            return True
        return False

    def draw(self, surface):
        # Effet de pulsation
        pulse = abs(math.sin(self.pulse_timer * 0.05)) * 10
        if pulse > 5:
            pulse_surf = pygame.Surface((self.size + 40, self.size + 40), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, (150, 150, 150, 50),
                             (self.size//2 + 20, self.size//2 + 20),
                             int(self.size//2 + pulse))
            surface.blit(pulse_surf, (self.rect.centerx - self.size//2 - 20,
                                      self.rect.centery - self.size//2 - 20))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)
