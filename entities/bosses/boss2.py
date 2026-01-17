import pygame
import random
import math

from config import SCREEN_WIDTH, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss2Projectile


class Boss2(Enemy):
    """Second Boss - Plus agressif avec des patterns differents"""
    def __init__(self, x, y, speed=2, target_y=120):
        super().__init__(x, y, speed)

        self.size = 120
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 30
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 15
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 240
        self.lateral_movement_speed = 3
        self.lateral_direction = 1

        self.damage_animation_active = False
        self.damage_animation_duration = 20
        self.damage_animation_timer = 0
        self.damage_flash_interval = 4

        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 200
        self.death_explosion_timer = 0
        self.death_explosion_interval = 8
        self.death_explosions = []

        self.spiral_angle = 0
        self.laser_charging = False
        self.laser_charge_timer = 0
        self.laser_active = False
        self.laser_duration = 60
        self.laser_timer = 0

        self.pulse_timer = 0

    def _create_boss_sprite(self):
        """Cree un sprite procedural pour le Boss 2"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        points = []
        for i in range(6):
            angle = math.radians(60 * i - 90)
            radius = 50
            x = center + math.cos(angle) * radius
            y = center + math.sin(angle) * radius
            points.append((x, y))
        pygame.draw.polygon(surf, (80, 0, 120), points)
        pygame.draw.polygon(surf, (150, 0, 200), points, 3)

        pygame.draw.circle(surf, (255, 0, 0), (center - 20, center - 10), 12)
        pygame.draw.circle(surf, (255, 0, 0), (center + 20, center - 10), 12)
        pygame.draw.circle(surf, (255, 255, 0), (center - 20, center - 10), 6)
        pygame.draw.circle(surf, (255, 255, 0), (center + 20, center - 10), 6)

        pygame.draw.line(surf, (255, 0, 0), (center - 25, center + 20), (center + 25, center + 20), 3)

        return surf

    def _create_damaged_sprite(self):
        """Cree un sprite endommage"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 100))
        surf.blit(flash, (0, 0))
        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1

        if self.is_dying:
            self.death_animation_timer += 1

            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 3) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(2, int(12 * (1 - progress * 0.8)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(10, self.size - 10)
                rand_y = self.rect.top + random.randint(10, self.size - 10)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=400))

            for exp in self.death_explosions:
                exp.update()
            self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

            if self.death_animation_timer >= self.death_animation_duration:
                return True
            return False

        if self.damage_animation_active:
            self.damage_animation_timer += 1
            if (self.damage_animation_timer // self.damage_flash_interval) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self._create_boss_sprite()

        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 2 en position de combat!")
        else:
            self.rect.x += self.lateral_direction * self.lateral_movement_speed
            if self.rect.left <= 50 or self.rect.right >= SCREEN_WIDTH - 50:
                self.lateral_direction *= -1

            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 5
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles selon le pattern"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 10

        if pattern_index == 0:
            self.spiral_angle += 30
            for i in range(3):
                angle = math.radians(self.spiral_angle + i * 120)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=5))
            print("Boss 2: Tir spiral!")

        elif pattern_index == 1:
            # Pattern en V - les tirs descendent en diagonale depuis les côtés
            # Laisse un gap au centre et sur les côtés pour esquiver
            angles = [-45, -25, 25, 45]  # Angles en degrés (pas de tir central)
            for angle_deg in angles:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)  # cos pour que l'angle 0 soit vers le bas
                projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=6))
            print("Boss 2: Pluie de feu en V!")

        elif pattern_index == 2:
            for angle_deg in [-60, -40, -20]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(Boss2Projectile(bx - 30, by, dx, dy, speed=6))
            for angle_deg in [20, 40, 60]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(Boss2Projectile(bx + 30, by, dx, dy, speed=6))
            print("Boss 2: Double vague!")

        elif pattern_index == 3:
            cross_angle = (self.timer * 3) % 360
            for i in range(4):
                angle = math.radians(cross_angle + i * 90)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=6))
            print("Boss 2: Croix rotative!")

        elif pattern_index == 4:
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=9))
            for offset in [-10, 10]:
                angle = math.atan2(dy, dx) + math.radians(offset)
                ndx = math.cos(angle)
                ndy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, ndx, ndy, speed=8))
            print("Boss 2: Rafale ciblee!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des degats au boss et declenche l'animation"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer * 0.05)) * 0.2 + 0.8

        if not self.is_dying:
            aura_size = int(70 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (100, 0, 150, 50), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)
