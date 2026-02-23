import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss4Projectile, BouncingProjectile, SplittingProjectile


class Boss4(Enemy):
    """Quatrieme Boss - Boss final ultime avec des patterns complexes"""
    def __init__(self, x, y, speed=2, target_y=80):
        super().__init__(x, y, speed)

        self.size = 160
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 50
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 10
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 180
        self.lateral_movement_speed = 2.5
        self.lateral_direction = 1

        self.movement_angle = 0
        self.movement_radius_x = 150
        self.movement_radius_y = 40

        self.damage_animation_active = False
        self.damage_animation_duration = 12
        self.damage_animation_timer = 0
        self.damage_flash_interval = 2

        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 300
        self.death_explosion_timer = 0
        self.death_explosions = []

        self.vortex_angle = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 180
        self.shield_cooldown = 600
        self.last_shield_time = -600

        self.charging = False
        self.charge_timer = 0
        self.charge_duration = 120
        self.charge_warning_duration = 60
        self.original_y = 0
        self.original_x = 0
        self.swoop_phase = 0  # 0=warning, 1=centering, 2=swoop curve
        self.swoop_angle = 0.0  # angle along the swoop ellipse
        self.swoop_center_x = SCREEN_WIDTH // 2  # cible X pour le centrage
        self.swoop_centering_speed = 3
        self.swoop_shots_fired = 0  # nombre de salves tirées pendant le swoop (0, 1, 2, 3)

        self.pulse_timer = 0
        self.ring_rotation = 0
        self.inner_rotation = 0

    def _create_boss_sprite(self):
        """Cree un sprite procedural pour le Boss 4 - Soleil/Etoile divine"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        for i in range(12):
            angle = math.radians(30 * i)
            inner_radius = 40
            outer_radius = 70
            x1 = center + math.cos(angle) * inner_radius
            y1 = center + math.sin(angle) * inner_radius
            x2 = center + math.cos(angle) * outer_radius
            y2 = center + math.sin(angle) * outer_radius
            pygame.draw.line(surf, (255, 200, 0), (x1, y1), (x2, y2), 4)

        pygame.draw.circle(surf, (180, 120, 0), (center, center), 45)
        pygame.draw.circle(surf, (255, 200, 50), (center, center), 40)
        pygame.draw.circle(surf, (255, 215, 0), (center, center), 45, 3)

        triangle_size = 25
        triangle_points = []
        for i in range(3):
            angle = math.radians(120 * i - 90)
            tx = center + math.cos(angle) * triangle_size
            ty = center + math.sin(angle) * triangle_size
            triangle_points.append((tx, ty))
        pygame.draw.polygon(surf, (200, 100, 0), triangle_points)
        pygame.draw.polygon(surf, (255, 150, 0), triangle_points, 2)

        pygame.draw.circle(surf, (255, 50, 0), (center, center), 15)
        pygame.draw.circle(surf, (255, 255, 0), (center, center), 10)
        pygame.draw.circle(surf, WHITE, (center, center), 5)

        return surf

    def _create_damaged_sprite(self):
        """Cree un sprite endommage"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 150))
        surf.blit(flash, (0, 0))
        return surf

    def _create_shield_sprite(self):
        """Cree un sprite avec bouclier"""
        surf = self._create_boss_sprite()
        shield_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (255, 215, 0, 100), (self.size//2, self.size//2), 75)
        pygame.draw.circle(shield_surf, (255, 255, 200, 200), (self.size//2, self.size//2), 75, 3)
        surf.blit(shield_surf, (0, 0))
        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1
        self.ring_rotation += 1
        self.inner_rotation -= 0.5

        if self.is_dying:
            self.death_animation_timer += 1
            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 2) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(1, int(8 * (1 - progress * 0.95)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(0, self.size)
                rand_y = self.rect.top + random.randint(0, self.size)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=600))

            for exp in self.death_explosions:
                exp.update()
            self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

            if self.death_animation_timer >= self.death_animation_duration:
                return True
            return False

        if self.shield_active:
            self.shield_timer += 1
            self.image = self._create_shield_sprite()
            if self.shield_timer >= self.shield_duration:
                self.shield_active = False
                self.shield_timer = 0
                self.last_shield_time = self.timer
                self.image = self._create_boss_sprite()
        elif self.damage_animation_active:
            self.damage_animation_timer += 1
            if (self.damage_animation_timer // self.damage_flash_interval) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self._create_boss_sprite()

        if self.charging:
            self.charge_timer += 1
            if self.swoop_phase == 0:
                # Phase d'annonce : tremblement
                if self.charge_timer <= self.charge_warning_duration:
                    shake = random.randint(-3, 3)
                    self.rect.x += shake
                else:
                    # Passer au centrage fluide
                    self.swoop_phase = 1
                    self.swoop_center_x = SCREEN_WIDTH // 2
            elif self.swoop_phase == 1:
                # Phase de centrage : le boss se déplace fluidement vers le centre
                diff_x = self.swoop_center_x - self.rect.centerx
                diff_y = self.target_y - self.rect.centery
                if abs(diff_x) <= self.swoop_centering_speed and abs(diff_y) <= self.swoop_centering_speed:
                    self.rect.centerx = self.swoop_center_x
                    self.rect.centery = self.target_y
                    self.swoop_phase = 2
                    self.swoop_angle = 0.0
                    self.original_x = self.rect.centerx
                    self.original_y = self.rect.centery
                else:
                    if abs(diff_x) > self.swoop_centering_speed:
                        self.rect.centerx += self.swoop_centering_speed if diff_x > 0 else -self.swoop_centering_speed
                    else:
                        self.rect.centerx = self.swoop_center_x
                    if abs(diff_y) > self.swoop_centering_speed:
                        self.rect.centery += self.swoop_centering_speed if diff_y > 0 else -self.swoop_centering_speed
                    else:
                        self.rect.centery = self.target_y
            elif self.swoop_phase == 2:
                # Courbe style Angry Sun
                # L'ellipse est centrée en dessous du boss (original_y + radius_y)
                # Au début (angle=PI/2), sin=1 => y = center_y - radius_y = original_y (position de départ)
                # Puis le boss descend à gauche, passe en bas, remonte à droite
                swoop_speed = 0.035
                self.swoop_angle += swoop_speed
                radius_x = 300
                radius_y = 380
                center_y = self.original_y + radius_y  # centre de l'ellipse = en dessous du boss
                angle = math.pi / 2 - self.swoop_angle  # sens horaire
                self.rect.centerx = self.original_x - int(math.cos(angle) * radius_x)
                self.rect.centery = center_y - int(math.sin(angle) * radius_y)
                # Tirs en 8 directions à gauche (PI/2), en bas (PI), à droite (3*PI/2)
                if enemy_projectiles is not None:
                    shot_thresholds = [
                        math.pi / 4,      # haut-gauche
                        math.pi / 2,      # gauche
                        3 * math.pi / 4,  # bas-gauche
                        math.pi,          # bas
                        5 * math.pi / 4,  # bas-droite
                        3 * math.pi / 2,  # droite
                        7 * math.pi / 4,  # haut-droite
                    ]
                    if self.swoop_shots_fired < len(shot_thresholds) and self.swoop_angle >= shot_thresholds[self.swoop_shots_fired]:
                        bx, by = self.rect.centerx, self.rect.centery
                        for i in range(8):
                            a = math.radians(i * 45)
                            dx = math.cos(a)
                            dy = math.sin(a)
                            enemy_projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=5))
                        self.swoop_shots_fired += 1
                        print(f"Boss 4: Swoop burst {self.swoop_shots_fired}!")
                # Fin du swoop après un tour complet
                if self.swoop_angle >= 2 * math.pi:
                    self.charging = False
                    self.charge_timer = 0
                    self.swoop_phase = 0
                    self.swoop_angle = 0.0
                    # Resynchroniser movement_angle pour que le mouvement normal
                    # reprenne depuis le centre (sin(0)=0, sin(PI)=0)
                    self.movement_angle = 0.0
                    self.rect.centerx = self.original_x
                    self.rect.centery = self.original_y
            return False

        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                self.original_y = self.rect.centery
                print("Boss 4 en position de combat!")
        else:
            self.movement_angle += 0.02
            offset_x = math.sin(self.movement_angle) * self.movement_radius_x
            offset_y = math.sin(self.movement_angle * 2) * self.movement_radius_y
            self.rect.centerx = SCREEN_WIDTH // 2 + int(offset_x)
            self.rect.centery = self.target_y + int(offset_y)

            if self.hp < 25 and not self.shield_active and self.timer - self.last_shield_time >= self.shield_cooldown:
                self.shield_active = True
                self.shield_timer = 0
                print("Boss 4: Bouclier active!")

            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 7
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns ultimes du Boss 4"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 20

        if pattern_index == 0:
            self.vortex_angle += 25
            for i in range(4):
                angle = math.radians(self.vortex_angle + i * 90)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=4))
            print("Boss 4: Vortex!")

        elif pattern_index == 1:
            for angle_deg in [-35, -30, 0, 30, 35]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(BouncingProjectile(bx, by, dx, dy, speed=6, bounces=2))
            print("Boss 4: Tirs rebondissants!")

        elif pattern_index == 2:
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(SplittingProjectile(bx, by, dx, dy, speed=4, split_time=50))
            print("Boss 4: Tir diviseur!")

        elif pattern_index == 3:
            for i in range(9):
                offset_x = (i - 4) * 45
                delay_factor = abs(i - 4) * 0.1
                dy = 1
                dx = delay_factor * (1 if i > 4 else -1)
                projectiles.append(Boss4Projectile(bx + offset_x, by, dx, dy, speed=7))
            print("Boss 4: Pluie solaire!")

        elif pattern_index == 4:
            num_projectiles = 10
            for ring in range(2):
                offset = ring * 18
                for i in range(num_projectiles):
                    angle = (2 * math.pi / num_projectiles) * i + math.radians(offset)
                    dx = math.cos(angle)
                    dy = math.sin(angle)
                    speed = 4 if ring == 0 else 6
                    projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=speed))
            print("Boss 4: Double anneau!")

        elif pattern_index == 5:
            for i in range(5):
                angle = math.radians(72 * i - 90 + self.timer % 72)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=8))
                angle2 = angle + math.radians(36)
                dx2 = math.cos(angle2)
                dy2 = math.sin(angle2)
                projectiles.append(Boss4Projectile(bx, by, dx2, dy2, speed=5))
            print("Boss 4: Etoile filante!")

        elif pattern_index == 6:
            if not self.charging and self.timer % 300 < 10:
                self.charging = True
                self.charge_timer = 0
                self.swoop_phase = 0
                self.swoop_angle = 0.0
                self.original_x = self.rect.centerx
                self.original_y = self.rect.centery
                self.swoop_shots_fired = 0
                print("Boss 4: SWOOP!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des degats au boss (bloque si bouclier actif)"""
        if self.shield_active:
            print("Boss 4: Bouclier absorbe les degats!")
            return
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer * 0.04)) * 0.3 + 0.7
        cx, cy = self.rect.centerx, self.rect.centery

        if not self.is_dying:
            aura_size = int(90 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 200, 0, 30), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (cx - aura_size, cy - aura_size))

            for i in range(3):
                ring_radius = 85 + i * 15
                ring_alpha = 100 - i * 30
                ring_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (255, 215, 0, ring_alpha),
                                 (ring_radius + 5, ring_radius + 5), ring_radius, 2)
                rotated = pygame.transform.rotate(ring_surf, self.ring_rotation * (i + 1) * 0.5)
                rot_rect = rotated.get_rect(center=(cx, cy))
                surface.blit(rotated, rot_rect)

            for i in range(6):
                angle = math.radians(self.ring_rotation * 2 + i * 60)
                orb_x = cx + math.cos(angle) * 80
                orb_y = cy + math.sin(angle) * 50
                pygame.draw.circle(surface, (255, 200, 0), (int(orb_x), int(orb_y)), 6)
                pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), 3)

        if self.charging and (self.swoop_phase == 0 or self.swoop_phase == 1):
            warning_alpha = int(200 * abs(math.sin(self.charge_timer * 0.4)))

            # Tracé de la trajectoire elliptique en pointillés
            trajectory_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Le swoop part du centre de l'écran (après centrage)
            ellipse_cx = SCREEN_WIDTH // 2
            ellipse_cy = self.target_y + 380  # target_y + radius_y
            radius_x = 300
            radius_y = 380
            # Dessiner des points le long de l'ellipse
            num_points = 60
            progress = self.charge_timer / self.charge_warning_duration if self.swoop_phase == 0 else 1.0
            visible_points = int(num_points * min(1.0, progress * 1.5))
            for i in range(visible_points):
                t = i / num_points
                angle = math.pi / 2 - t * 2 * math.pi  # sens horaire depuis le haut
                px = ellipse_cx - int(math.cos(angle) * radius_x)
                py = ellipse_cy - int(math.sin(angle) * radius_y)
                # Pointillés : un point sur deux
                if i % 2 == 0:
                    dot_alpha = int(warning_alpha * (0.4 + 0.6 * (1 - t)))
                    pygame.draw.circle(trajectory_surf, (255, 180, 50, dot_alpha), (px, py), 3)

            # Flèche directionnelle animée le long du trajet
            arrow_t = (self.charge_timer * 0.02) % 1.0
            arrow_angle = math.pi / 2 - arrow_t * 2 * math.pi
            arrow_x = ellipse_cx - int(math.cos(arrow_angle) * radius_x)
            arrow_y = ellipse_cy - int(math.sin(arrow_angle) * radius_y)
            pygame.draw.circle(trajectory_surf, (255, 255, 150, warning_alpha), (arrow_x, arrow_y), 6)
            pygame.draw.circle(trajectory_surf, (255, 255, 255, warning_alpha), (arrow_x, arrow_y), 3)

            surface.blit(trajectory_surf, (0, 0))

            # Flash au centre du boss
            flash_r = int(60 + math.sin(self.charge_timer * 0.6) * 20)
            flash_surf = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 200, int(warning_alpha * 0.5)),
                             (flash_r, flash_r), flash_r)
            surface.blit(flash_surf, (cx - flash_r, cy - flash_r))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)
