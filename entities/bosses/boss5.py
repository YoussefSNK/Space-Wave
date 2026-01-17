import pygame
import random
import math

from config import SCREEN_WIDTH, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss5Projectile, ZigZagProjectile, GravityProjectile, TeleportingProjectile


class Boss5(Enemy):
    """Cinquieme Boss - Le Nemesis ultime avec des patterns chaotiques"""
    def __init__(self, x, y, speed=2, target_y=90):
        super().__init__(x, y, speed)

        self.size = 180
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 60
        self.max_hp = 60
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 8
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 150

        self.teleport_cooldown = 240
        self.last_teleport = -240
        self.is_teleporting = False
        self.teleport_timer = 0
        self.teleport_duration = 30
        self.teleport_target = (0, 0)

        self.damage_animation_active = False
        self.damage_animation_duration = 10
        self.damage_animation_timer = 0
        self.damage_flash_interval = 2

        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 360
        self.death_explosion_timer = 0
        self.death_explosions = []

        self.rage_mode = False
        self.rage_pulse = 0

        self.clone_active = False
        self.clone_position = (0, 0)
        self.clone_timer = 0
        self.clone_duration = 180

        self.shield_orbs = []
        self.shield_active = False
        self.shield_orb_count = 6
        self.shield_rotation = 0

        self.pulse_timer = 0
        self.eye_glow = 0

    def _create_boss_sprite(self):
        """Cree un sprite procedural pour le Boss 5 - Entite cosmique/Oeil du chaos"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        for i in range(8):
            angle = math.radians(45 * i + 22.5)
            for j in range(3):
                length = 60 + j * 15
                thickness = 6 - j * 2
                x1 = center + math.cos(angle) * 35
                y1 = center + math.sin(angle) * 35
                x2 = center + math.cos(angle) * length
                y2 = center + math.sin(angle) * length
                color_intensity = 150 + j * 35
                pygame.draw.line(surf, (0, color_intensity, int(color_intensity * 0.5)),
                               (x1, y1), (x2, y2), thickness)

        pygame.draw.circle(surf, (20, 60, 40), (center, center), 50)
        pygame.draw.circle(surf, (30, 100, 60), (center, center), 45)
        pygame.draw.circle(surf, (0, 150, 80), (center, center), 50, 3)

        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            hx = center + math.cos(angle) * 30
            hy = center + math.sin(angle) * 30
            hex_points.append((hx, hy))
        pygame.draw.polygon(surf, (0, 80, 50), hex_points)
        pygame.draw.polygon(surf, (0, 200, 100), hex_points, 2)

        pygame.draw.circle(surf, (0, 0, 0), (center, center), 22)
        pygame.draw.circle(surf, (0, 255, 100), (center, center), 18)
        pygame.draw.circle(surf, (200, 255, 200), (center, center), 10)
        pygame.draw.circle(surf, (0, 100, 50), (center, center), 5)

        for i in range(3):
            angle = math.radians(120 * i - 90)
            ex = center + math.cos(angle) * 35
            ey = center + math.sin(angle) * 35
            pygame.draw.circle(surf, (0, 0, 0), (int(ex), int(ey)), 8)
            pygame.draw.circle(surf, (0, 255, 100), (int(ex), int(ey)), 6)
            pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 3)

        return surf

    def _create_damaged_sprite(self):
        """Cree un sprite endommage"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 180))
        surf.blit(flash, (0, 0))
        return surf

    def _create_rage_sprite(self):
        """Cree un sprite en mode rage"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        for i in range(8):
            angle = math.radians(45 * i + 22.5 + self.rage_pulse)
            for j in range(4):
                length = 65 + j * 18
                thickness = 7 - j * 1.5
                x1 = center + math.cos(angle) * 35
                y1 = center + math.sin(angle) * 35
                x2 = center + math.cos(angle) * length
                y2 = center + math.sin(angle) * length
                pygame.draw.line(surf, (255, int(50 + j * 30), 0),
                               (x1, y1), (x2, y2), int(thickness))

        pygame.draw.circle(surf, (80, 20, 20), (center, center), 50)
        pygame.draw.circle(surf, (150, 30, 30), (center, center), 45)
        pygame.draw.circle(surf, (255, 50, 50), (center, center), 50, 3)

        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30 + self.rage_pulse * 2)
            hx = center + math.cos(angle) * 30
            hy = center + math.sin(angle) * 30
            hex_points.append((hx, hy))
        pygame.draw.polygon(surf, (100, 0, 0), hex_points)
        pygame.draw.polygon(surf, (255, 100, 0), hex_points, 2)

        pygame.draw.circle(surf, (0, 0, 0), (center, center), 22)
        pygame.draw.circle(surf, (255, 50, 0), (center, center), 18)
        pygame.draw.circle(surf, (255, 200, 100), (center, center), 10)
        pygame.draw.circle(surf, (150, 0, 0), (center, center), 5)

        for i in range(3):
            angle = math.radians(120 * i - 90 + self.rage_pulse)
            ex = center + math.cos(angle) * 35
            ey = center + math.sin(angle) * 35
            pygame.draw.circle(surf, (0, 0, 0), (int(ex), int(ey)), 8)
            pygame.draw.circle(surf, (255, 50, 0), (int(ex), int(ey)), 6)
            pygame.draw.circle(surf, (255, 200, 0), (int(ex), int(ey)), 3)

        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1
        self.eye_glow = abs(math.sin(self.pulse_timer * 0.05)) * 50

        if self.hp <= self.max_hp * 0.3 and not self.rage_mode:
            self.rage_mode = True
            self.shoot_delay_frames = 5
            print("Boss 5: MODE RAGE ACTIVE!")

        if self.rage_mode:
            self.rage_pulse += 3

        if self.is_dying:
            self.death_animation_timer += 1
            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 2) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_rage_sprite() if self.rage_mode else self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(1, int(6 * (1 - progress * 0.98)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(-20, self.size + 20)
                rand_y = self.rect.top + random.randint(-20, self.size + 20)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=700))

            for exp in self.death_explosions:
                exp.update()
            self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

            if self.death_animation_timer >= self.death_animation_duration:
                return True
            return False

        if self.is_teleporting:
            self.teleport_timer += 1
            if self.teleport_timer >= self.teleport_duration // 2 and self.rect.center != self.teleport_target:
                self.rect.center = self.teleport_target
            if self.teleport_timer >= self.teleport_duration:
                self.is_teleporting = False
                self.teleport_timer = 0
            return False

        if self.damage_animation_active:
            self.damage_animation_timer += 1
            if (self.damage_animation_timer // self.damage_flash_interval) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_rage_sprite() if self.rage_mode else self._create_boss_sprite()

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self._create_rage_sprite() if self.rage_mode else self._create_boss_sprite()
        else:
            self.image = self._create_rage_sprite() if self.rage_mode else self._create_boss_sprite()

        if self.clone_active:
            self.clone_timer += 1
            if self.clone_timer >= self.clone_duration:
                self.clone_active = False
                self.clone_timer = 0

        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 5 en position de combat!")
        else:
            move_x = math.sin(self.timer * 0.03) * 3 + math.cos(self.timer * 0.02) * 2
            move_y = math.cos(self.timer * 0.025) * 2
            self.rect.x += int(move_x)
            self.rect.y = self.target_y + int(math.sin(self.timer * 0.015) * 40)

            self.rect.x = max(100, min(SCREEN_WIDTH - 100, self.rect.x))

            tp_cooldown = self.teleport_cooldown // 2 if self.rage_mode else self.teleport_cooldown
            if self.timer - self.last_teleport >= tp_cooldown and player_position:
                self.is_teleporting = True
                self.teleport_timer = 0
                self.last_teleport = self.timer
                self.teleport_target = (
                    random.randint(150, SCREEN_WIDTH - 150),
                    random.randint(80, 200)
                )
                print("Boss 5: Teleportation!")

            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    num_patterns = 8 if self.rage_mode else 6
                    pattern_index = (self.timer // self.pattern_switch_interval) % num_patterns
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns chaotiques du Boss 5"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 30

        if pattern_index == 0:
            for i in range(5):
                offset_x = (i - 2) * 50
                projectiles.append(ZigZagProjectile(bx + offset_x, by, 1, speed=5,
                                                   amplitude=40 + i * 10, frequency=0.08 + i * 0.02))
            print("Boss 5: Zigzag!")

        elif pattern_index == 1:
            for angle_deg in [-60, -30, 0, 30, 60]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad) * 0.3
                projectiles.append(GravityProjectile(bx, by, dx, dy, speed=6))
            print("Boss 5: Tirs paraboliques!")

        elif pattern_index == 2:
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(TeleportingProjectile(bx, by, dx, dy, speed=3))
            projectiles.append(TeleportingProjectile(bx - 30, by, dx, dy, speed=3))
            projectiles.append(TeleportingProjectile(bx + 30, by, dx, dy, speed=3))
            print("Boss 5: Tirs teleporteurs!")

        elif pattern_index == 3:
            for i in range(6):
                angle1 = math.radians(self.timer * 4 + i * 60)
                angle2 = math.radians(-self.timer * 4 + i * 60 + 30)
                dx1 = math.cos(angle1)
                dy1 = math.sin(angle1)
                dx2 = math.cos(angle2)
                dy2 = math.sin(angle2)
                projectiles.append(Boss5Projectile(bx, by, dx1, dy1, speed=4))
                projectiles.append(Boss5Projectile(bx, by, dx2, dy2, speed=4))
            print("Boss 5: Double spirale!")

        elif pattern_index == 4:
            for i in range(11):
                offset_x = (i - 5) * 40
                wave_offset = math.sin(i * 0.5 + self.timer * 0.1) * 0.3
                projectiles.append(Boss5Projectile(bx + offset_x, by, wave_offset, 1, speed=6))
            print("Boss 5: Mur ondulant!")

        elif pattern_index == 5:
            if not self.clone_active:
                self.clone_active = True
                self.clone_timer = 0
                self.clone_position = (SCREEN_WIDTH - self.rect.centerx, self.rect.centery)
                print("Boss 5: Clone active!")
            cx, cy = self.clone_position
            px, py = player_position
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(Boss5Projectile(cx, cy + 60, dx, dy, speed=7))

        elif pattern_index == 6 and self.rage_mode:
            for i in range(16):
                angle = (2 * math.pi / 16) * i + self.timer * 0.1
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss5Projectile(bx, by, dx, dy, speed=5))
            print("Boss 5: TEMPETE!")

        elif pattern_index == 7 and self.rage_mode:
            projectiles.append(ZigZagProjectile(bx, by, 1, speed=6, amplitude=60, frequency=0.1))
            projectiles.append(GravityProjectile(bx - 50, by, -0.3, 0.2, speed=5))
            projectiles.append(GravityProjectile(bx + 50, by, 0.3, 0.2, speed=5))
            for i in range(4):
                angle = math.radians(self.timer * 5 + i * 90)
                projectiles.append(Boss5Projectile(bx, by, math.cos(angle), math.sin(angle), speed=4))
            print("Boss 5: CHAOS TOTAL!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des degats au boss"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer * 0.03)) * 0.4 + 0.6

        if not self.is_dying:
            if self.rage_mode:
                aura_color = (150, 0, 0, 40)
            else:
                aura_color = (0, 150, 50, 40)
            aura_size = int(100 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color, (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            for i in range(8):
                angle = math.radians(self.pulse_timer * 1.5 + i * 45)
                radius = 90 + math.sin(self.pulse_timer * 0.05 + i) * 20
                px = self.rect.centerx + math.cos(angle) * radius
                py = self.rect.centery + math.sin(angle) * radius * 0.6
                color = (255, 100, 0) if self.rage_mode else (0, 255, 100)
                pygame.draw.circle(surface, color, (int(px), int(py)), 5)
                pygame.draw.circle(surface, WHITE, (int(px), int(py)), 2)

        if self.is_teleporting:
            alpha = int(255 * (1 - self.teleport_timer / self.teleport_duration))
            tp_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            tp_surf.blit(self.image, (0, 0))
            tp_surf.set_alpha(alpha)
            surface.blit(tp_surf, self.rect)
            if self.teleport_timer >= self.teleport_duration // 2:
                target_alpha = int(255 * (self.teleport_timer - self.teleport_duration // 2) / (self.teleport_duration // 2))
                arrival_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                arrival_surf.blit(self.image, (0, 0))
                arrival_surf.set_alpha(target_alpha)
                arrival_rect = arrival_surf.get_rect(center=self.teleport_target)
                surface.blit(arrival_surf, arrival_rect)
            return

        if self.clone_active:
            clone_alpha = int(150 + 50 * math.sin(self.clone_timer * 0.1))
            clone_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            clone_surf.blit(self.image, (0, 0))
            clone_surf.set_alpha(clone_alpha)
            clone_rect = clone_surf.get_rect(center=self.clone_position)
            surface.blit(clone_surf, clone_rect)

        surface.blit(self.image, self.rect)

        if self.rage_mode:
            rage_text_surf = pygame.Surface((100, 20), pygame.SRCALPHA)
            rage_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.1)))
            pygame.draw.rect(rage_text_surf, (255, 0, 0, rage_alpha), (0, 0, 100, 20))
            surface.blit(rage_text_surf, (self.rect.centerx - 50, self.rect.top - 30))

        for exp in self.death_explosions:
            exp.draw(surface)
