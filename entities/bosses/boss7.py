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
        self.pattern_timer = -59       # Démarre à -59 → 1s de délai initial, puis pattern toutes les 5s
        self.pattern_step = 0          # Sous-étape dans le pattern actif (Pattern 2)
        self.pattern_step_timer = 0    # Timer entre deux sous-étapes (Pattern 2)
        self.arrived = False           # True dès que le boss a atteint target_y une première fois
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
        if not self.arrived and self.rect.centery < self.target_y:
            self.rect.y += self.speed
        else:
            if not self.arrived:
                self.arrived = True
                print(f"[Boss7] Arrivé en position (timer={self.timer})")

            # Mouvement lateral fluide
            offset_x = math.sin(self.movement_angle) * self.movement_amplitude
            offset_y = math.cos(self.movement_angle * 0.7) * (self.movement_amplitude * 0.3)
            base_x = SCREEN_WIDTH // 2 + offset_x

            self.rect.centerx = int(base_x)
            self.rect.centery = int(self.target_y + offset_y)

            # Gestion des patterns (chaque pattern dure 5s = 300 frames)
            self.pattern_timer += 1

            if self.pattern_timer == 1:
                # Première frame du pattern : tir immédiat
                self.start_pattern(player_pos, projectiles_list)
            elif self.pattern_timer > 1:
                # Frames suivantes : mise à jour des patterns séquentiels
                self.update_pattern_sequence(projectiles_list)

            if self.pattern_timer >= 300:
                # Fin du pattern : passage au suivant
                self.pattern_timer = 0
                self.pattern_index = (self.pattern_index + 1) % 7
                self.pattern_step = 0
                self.pattern_step_timer = 0

        return False

    def start_pattern(self, player_pos, projectiles_list):
        """Tir immédiat à la première frame du pattern."""
        print(f"[Boss7] Pattern {self.pattern_index} déclenché (timer={self.timer})")
        cx, cy = self.rect.center
        if self.pattern_index == 0:
            self.pattern_ball_breaker_diagonal(projectiles_list)
        elif self.pattern_index == 1:
            self.pattern_step = 0
            self.pattern_step_timer = 0
            self._fire_wave_breaker_ball(projectiles_list)
            self.pattern_step = 1
        elif self.pattern_index == 2:
            # Éventail : 8 balles en éventail vers le bas (200° à 340°, pas de 20°)
            for angle in range(200, 360, 20):
                self._fire_ball_at(cx, cy, angle, projectiles_list)
        elif self.pattern_index == 3:
            # Orbite : première balle de la rotation (270° = droit vers le bas)
            self._fire_ball_at(cx, cy, 270, projectiles_list)
            self.pattern_step = 1
            self.pattern_step_timer = 0
        elif self.pattern_index == 4:
            # Nova : première salve de 8 balles dans toutes les directions
            for angle in range(0, 360, 45):
                self._fire_ball_at(cx, cy, angle, projectiles_list)
            self.pattern_step = 1
            self.pattern_step_timer = 0
        elif self.pattern_index == 5:
            # Mix : 2 Edge Rollers + 2 Curve Stalkers, un de chaque côté
            px, py = player_pos
            for side, offset in [("left", -60), ("right", 60)]:
                sx = cx + offset
                projectiles_list.append(EdgeRollerProjectile(sx, cy, px, py, speed=9))
                projectiles_list.append(CurveStalkerProjectile(
                    sx, cy, self.rect.left, self.rect.right, side, speed=6.5
                ))
        elif self.pattern_index == 6:
            # Vague inversée : première balle depuis la droite (310°)
            self._fire_ball_at(cx + 100, cy, 310, projectiles_list)
            self.pattern_step = 1
            self.pattern_step_timer = 0

    def update_pattern_sequence(self, projectiles_list):
        """Mise à jour des patterns séquentiels (frames 2+)."""
        if self.pattern_index == 1:
            self._update_wave_breaker(projectiles_list)
        elif self.pattern_index == 3:
            self._update_orbit(projectiles_list)
        elif self.pattern_index == 4:
            self._update_nova(projectiles_list)
        elif self.pattern_index == 6:
            self._update_reverse_wave(projectiles_list)

    def _update_wave_breaker(self, projectiles_list):
        """Pattern 2 : tire les balles restantes une par une toutes les 0.5s."""
        TOTAL_BALLS = 5
        STEP_DELAY = 30  # 0.5 secondes (60 FPS * 0.5)

        if self.pattern_step >= TOTAL_BALLS:
            return  # Toutes les balles tirées, on attend la fin du pattern (pattern_timer >= 300)

        self.pattern_step_timer += 1
        if self.pattern_step_timer >= STEP_DELAY:
            self.pattern_step_timer = 0
            self._fire_wave_breaker_ball(projectiles_list)
            self.pattern_step += 1

    def _fire_ball_at(self, spawn_x, spawn_y, angle_deg, projectiles_list, speed=8):
        """Helper : tire une Ball Breaker en direction angle_deg (convention math, y vers le haut)."""
        angle_rad = math.radians(angle_deg)
        target_x = spawn_x + math.cos(angle_rad) * 1000
        target_y = spawn_y - math.sin(angle_rad) * 1000
        proj = BallBreakerProjectile(spawn_x, spawn_y, target_x, target_y, speed=speed)
        projectiles_list.append(proj)

    def _fire_wave_breaker_ball(self, projectiles_list):
        """Tire une Ball Breaker dans la direction ondulée correspondant à l'étape actuelle."""
        ANGLES = [230, 250, 270, 290, 310]
        cx, cy = self.rect.center
        step = self.pattern_step
        spawn_x = cx - 100 + step * 50  # Gauche à droite : -100, -50, 0, +50, +100
        self._fire_ball_at(spawn_x, cy, ANGLES[step], projectiles_list)

    def _update_orbit(self, projectiles_list):
        """Pattern 4 (Orbite) : 12 balles en rotation complète, une toutes les 22 frames."""
        TOTAL_BALLS = 12
        STEP_DELAY = 22   # ~0.37s
        START_ANGLE = 270
        STEP_ANGLE = -30  # Sens horaire sur l'écran

        if self.pattern_step >= TOTAL_BALLS:
            return

        self.pattern_step_timer += 1
        if self.pattern_step_timer >= STEP_DELAY:
            self.pattern_step_timer = 0
            angle = (START_ANGLE + self.pattern_step * STEP_ANGLE) % 360
            cx, cy = self.rect.center
            self._fire_ball_at(cx, cy, angle, projectiles_list)
            self.pattern_step += 1

    def _update_nova(self, projectiles_list):
        """Pattern 5 (Nova) : seconde salve de 8 balles tirée 2.5s après la première."""
        if self.pattern_step == 1:
            self.pattern_step_timer += 1
            if self.pattern_step_timer >= 150:
                cx, cy = self.rect.center
                for angle in range(0, 360, 45):
                    self._fire_ball_at(cx, cy, angle, projectiles_list)
                self.pattern_step = 2

    def _update_reverse_wave(self, projectiles_list):
        """Pattern 7 (Vague inversée) : 5 balles de droite à gauche, puis une 6e rapide à 210°."""
        ANGLES   = [290, 270, 250, 230]          # Steps 1-4 (step 0 déjà tiré dans start_pattern)
        SPAWNS_X = [50,  0,  -50, -100]          # Offsets cx : +50, 0, -50, -100
        STEP_DELAY = 6  # 0.1 secondes

        self.pattern_step_timer += 1
        if self.pattern_step_timer < STEP_DELAY:
            return
        self.pattern_step_timer = 0

        cx, cy = self.rect.center

        if self.pattern_step <= len(ANGLES):
            # Balles 2 à 5 (steps 1-4)
            idx = self.pattern_step - 1
            self._fire_ball_at(cx + SPAWNS_X[idx], cy, ANGLES[idx], projectiles_list)
            self.pattern_step += 1
        elif self.pattern_step == len(ANGLES) + 1:
            # 6e balle : rapide à 210°, tirée depuis la gauche
            self._fire_ball_at(cx - 50, cy, 210, projectiles_list, speed=14)
            self.pattern_step += 1

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
