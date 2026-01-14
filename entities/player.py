import pygame
import random
import math

from config import YELLOW, SCREEN_WIDTH, SCREEN_HEIGHT
from .projectiles import Projectile, SpreadProjectile, RicochetProjectile
from resource_path import resource_path


class Player:
    def __init__(self, x, y, player_id=1, is_local=True, headless=False):
        self.player_id = player_id
        self.is_local = is_local
        self.headless = headless  # Mode sans graphiques (pour le serveur)

        # Charger le sprite seulement si on n'est pas en mode headless
        if not headless:
            try:
                self.image = pygame.image.load(resource_path("sprites/Spaceship.png")).convert_alpha()
                self.image = pygame.transform.scale(self.image, (50, 50))

                # Joueur 2 : teinte bleue pour le différencier
                if player_id == 2:
                    self.image = self._tint_image(self.image, (100, 150, 255))

                self.rect = self.image.get_rect(center=(x, y))
            except Exception:
                # Fallback si le sprite ne charge pas
                self.image = None
                self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
        else:
            self.image = None
            self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.hp = 10
        self.contact_damage = 1
        self.invulnerable = False
        self.invuln_duration = 500
        self.invuln_start = 0

        self.power_type = 'normal'  # 'normal', 'double', 'triple', 'spread'
        self.power_duration = 15000
        self.power_start = 0

        # Effet de reacteur (thruster)
        self.thruster_particles = []
        self.thruster_timer = 0

        # Contrôles clavier
        self.speed = 7
        self.dx = 0
        self.dy = 0
        self.wants_to_shoot = False

    def _tint_image(self, image, tint_color):
        """Applique une teinte de couleur au sprite."""
        tinted = image.copy()
        tint_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*tint_color, 100))
        tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return tinted

    def handle_input(self, keys):
        """Gère les inputs clavier (ZQSD + Espace)."""
        self.dx = 0
        self.dy = 0

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.dy = 1
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.dx = 1

        # Normaliser la diagonale
        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.707
            self.dy *= 0.707

        self.wants_to_shoot = keys[pygame.K_SPACE]

    def set_input(self, dx, dy, shoot):
        """Définit les inputs manuellement (pour le réseau)."""
        self.dx = dx
        self.dy = dy
        self.wants_to_shoot = shoot

    def update(self):
        # Appliquer le mouvement
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        # Garder le joueur dans l'écran
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.invulnerable:
            now = pygame.time.get_ticks()
            if now - self.invuln_start >= self.invuln_duration:
                self.invulnerable = False

        if self.power_type != 'normal':
            now = pygame.time.get_ticks()
            if now - self.power_start >= self.power_duration:
                self.power_type = 'normal'
                print("Power-up expire!")

        # Mise a jour de l'effet de reacteur
        self.thruster_timer += 1
        if self.thruster_timer % 2 == 0:
            # Creer de nouvelles particules de feu
            base_x = self.rect.centerx
            base_y = self.rect.bottom - 5
            for _ in range(2):
                particle = {
                    'x': base_x + random.uniform(-8, 8),
                    'y': base_y,
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(2, 4),
                    'life': random.randint(10, 20),
                    'max_life': 20,
                    'size': random.uniform(3, 6),
                }
                self.thruster_particles.append(particle)

        # Mise a jour des particules existantes
        for p in self.thruster_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['size'] = max(0, p['size'] - 0.2)

        # Supprimer les particules mortes
        self.thruster_particles = [p for p in self.thruster_particles if p['life'] > 0]

    def apply_powerup(self, power_type):
        """Applique un power-up au joueur"""
        self.power_type = power_type
        self.power_start = pygame.time.get_ticks()
        print(f"Power-up '{power_type}' active!")

    def shoot(self, projectile_list):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            cx, cy = self.rect.centerx, self.rect.top

            if self.power_type == 'normal':
                projectile_list.append(Projectile(cx, cy))

            elif self.power_type == 'double':
                offset = 15
                projectile_list.append(Projectile(cx - offset, cy))
                projectile_list.append(Projectile(cx + offset, cy))

            elif self.power_type == 'triple':
                offset = 20
                projectile_list.append(Projectile(cx - offset, cy))
                projectile_list.append(Projectile(cx, cy))
                projectile_list.append(Projectile(cx + offset, cy))

            elif self.power_type == 'spread':
                projectile_list.append(SpreadProjectile(cx, cy, angle=-15))
                projectile_list.append(Projectile(cx, cy))
                projectile_list.append(SpreadProjectile(cx, cy, angle=15))

            elif self.power_type == 'ricochet':
                projectile_list.append(RicochetProjectile(cx, cy))

            self.last_shot = now

    def draw(self, surface):
        # Dessiner l'effet de reacteur (avant le vaisseau)
        for p in self.thruster_particles:
            progress = p['life'] / p['max_life']
            size = int(p['size'])
            if size < 1:
                continue

            # Couleur qui passe de jaune/blanc (centre) a orange puis rouge
            if progress > 0.7:
                # Coeur chaud : jaune-blanc
                r, g, b = 255, 255, int(200 * progress)
            elif progress > 0.4:
                # Orange
                r, g, b = 255, int(150 + 100 * progress), 0
            else:
                # Rouge qui s'estompe
                r, g, b = int(255 * progress * 2), int(50 * progress), 0

            alpha = int(255 * progress)
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (r, g, b, alpha), (size, size), size)
            surface.blit(particle_surf, (int(p['x'] - size), int(p['y'] - size)))

        if self.invulnerable:
            temp_img = self.image.copy()
            pygame.draw.rect(temp_img, YELLOW, temp_img.get_rect(), 3)
            surface.blit(temp_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

        if self.power_type != 'normal':
            time_left = self.power_duration - (pygame.time.get_ticks() - self.power_start)
            progress = time_left / self.power_duration
            bar_width = 50
            bar_height = 5
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.bottom + 10

            from config import WHITE, CYAN
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            if self.power_type == 'double':
                color = CYAN
            elif self.power_type == 'triple':
                color = (255, 0, 255)
            elif self.power_type == 'spread':
                color = (0, 255, 100)
            elif self.power_type == 'ricochet':
                color = (255, 100, 0)  # Orange
            else:
                color = WHITE
            pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
