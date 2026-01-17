import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss3Projectile, HomingProjectile


class Boss3(Enemy):
    """Troisieme Boss - Le plus difficile avec des patterns complexes"""
    def __init__(self, x, y, speed=2, target_y=100):
        super().__init__(x, y, speed)

        self.size = 140
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 40
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 12
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 200
        self.lateral_movement_speed = 2
        self.lateral_direction = 1

        self.vertical_amplitude = 30
        self.vertical_frequency = 0.02

        self.damage_animation_active = False
        self.damage_animation_duration = 15
        self.damage_animation_timer = 0
        self.damage_flash_interval = 3

        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 240
        self.death_explosion_timer = 0
        self.death_explosions = []

        self.wave_angle = 0
        self.laser_warning_timer = 0
        self.laser_warning_duration = 60
        self.laser_active = False
        self.laser_timer = 0
        self.laser_duration = 90
        self.laser_target_x = 0

        self.teleport_cooldown = 300
        self.last_teleport = -300

        self.pulse_timer = 0
        self.core_rotation = 0

    def _create_boss_sprite(self):
        """Cree un sprite procedural pour le Boss 3 - forme de diamant/cristal"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        diamond_points = [
            (center, 10),
            (center + 55, center),
            (center, self.size - 10),
            (center - 55, center),
        ]
        pygame.draw.polygon(surf, (0, 80, 100), diamond_points)
        pygame.draw.polygon(surf, (0, 200, 255), diamond_points, 4)

        pygame.draw.line(surf, (0, 150, 200), (center, 10), (center, self.size - 10), 2)
        pygame.draw.line(surf, (0, 150, 200), (center - 55, center), (center + 55, center), 2)

        pygame.draw.circle(surf, (0, 255, 255), (center, center), 20)
        pygame.draw.circle(surf, WHITE, (center, center), 12)
        pygame.draw.circle(surf, (0, 100, 150), (center, center), 6)

        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            cx = center + math.cos(rad) * 35
            cy = center + math.sin(rad) * 35
            pygame.draw.circle(surf, (0, 200, 255), (int(cx), int(cy)), 8)
            pygame.draw.circle(surf, WHITE, (int(cx), int(cy)), 4)

        return surf

    def _create_damaged_sprite(self):
        """Cree un sprite endommage"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 120))
        surf.blit(flash, (0, 0))
        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1
        self.core_rotation += 2

        if self.is_dying:
            self.death_animation_timer += 1
            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 2) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(1, int(10 * (1 - progress * 0.9)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(5, self.size - 5)
                rand_y = self.rect.top + random.randint(5, self.size - 5)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=500))

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
                print("Boss 3 en position de combat!")
        else:
            self.rect.x += self.lateral_direction * self.lateral_movement_speed
            if self.rect.left <= 80 or self.rect.right >= SCREEN_WIDTH - 80:
                self.lateral_direction *= -1

            vertical_offset = math.sin(self.timer * self.vertical_frequency) * self.vertical_amplitude
            self.rect.centery = self.target_y + int(vertical_offset)

            if self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active = True
                    self.laser_timer = self.laser_duration

            if self.laser_active:
                self.laser_timer -= 1
                if self.laser_timer <= 0:
                    self.laser_active = False

            if player_position and enemy_projectiles is not None and not self.laser_active:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 6
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns uniques au Boss 3"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 20

        if pattern_index == 0:
            self.wave_angle += 15
            for i in range(7):
                offset = (i - 3) * 25
                angle = math.radians(self.wave_angle + i * 20)
                dy = 1
                dx = math.sin(angle) * 0.3
                projectiles.append(Boss3Projectile(bx + offset, by, dx, dy, speed=6))
            print("Boss 3: Vague sinusoidale!")

        elif pattern_index == 1:
            for angle_deg in [-45, -22, 0, 22, 45]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(Boss3Projectile(bx, by, dx, dy, speed=7))
            for angle_deg in [-45, -22, 0, 22, 45]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(Boss3Projectile(bx, by - 30, dx, dy, speed=5))
            print("Boss 3: Tir en X!")

        elif pattern_index == 2:
            projectiles.append(HomingProjectile(bx - 40, by, speed=3))
            projectiles.append(HomingProjectile(bx + 40, by, speed=3))
            print("Boss 3: Missiles guides!")

        elif pattern_index == 3:
            hole_position = random.randint(1, 5)
            for i in range(7):
                if i != hole_position and i != hole_position - 1:
                    offset_x = (i - 3) * 60
                    projectiles.append(Boss3Projectile(bx + offset_x, by, 0, 1, speed=5))
            print("Boss 3: Mur avec trou!")

        elif pattern_index == 4:
            num_projectiles = 12
            for i in range(num_projectiles):
                angle = (2 * math.pi / num_projectiles) * i
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss3Projectile(bx, by, dx, dy, speed=4))
            print("Boss 3: Explosion radiale!")

        elif pattern_index == 5:
            if self.laser_warning_timer == 0 and not self.laser_active:
                self.laser_warning_timer = self.laser_warning_duration
                self.laser_target_x = player_position[0]
                print("Boss 3: Laser en charge!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des degats au boss et declenche l'animation"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer * 0.03)) * 0.3 + 0.7

        if not self.is_dying:
            aura_size = int(80 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (0, 150, 200, 40), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            for i in range(4):
                angle = math.radians(self.core_rotation + i * 90)
                orb_x = self.rect.centerx + math.cos(angle) * 70
                orb_y = self.rect.centery + math.sin(angle) * 40
                pygame.draw.circle(surface, (0, 255, 255), (int(orb_x), int(orb_y)), 8)
                pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), 4)

        if self.laser_warning_timer > 0:
            warning_alpha = int(150 * abs(math.sin(self.laser_warning_timer * 0.3)))
            warning_surf = pygame.Surface((40, SCREEN_HEIGHT), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha))
            surface.blit(warning_surf, (self.laser_target_x - 20, 0))

        if self.laser_active:
            laser_width = 60
            laser_surf = pygame.Surface((laser_width, SCREEN_HEIGHT), pygame.SRCALPHA)
            for i in range(laser_width // 2):
                alpha = int(200 * (1 - i / (laser_width // 2)))
                pygame.draw.line(laser_surf, (0, 255, 255, alpha),
                               (laser_width // 2 - i, 0), (laser_width // 2 - i, SCREEN_HEIGHT))
                pygame.draw.line(laser_surf, (0, 255, 255, alpha),
                               (laser_width // 2 + i, 0), (laser_width // 2 + i, SCREEN_HEIGHT))
            pygame.draw.rect(laser_surf, WHITE, (laser_width // 2 - 5, 0, 10, SCREEN_HEIGHT))
            surface.blit(laser_surf, (self.laser_target_x - laser_width // 2, 0))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)
