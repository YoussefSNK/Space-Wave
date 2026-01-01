import pygame
import random
import math

from config import SCREEN_WIDTH
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import (
    Boss6Projectile, VortexProjectile, BlackHoleProjectile,
    MirrorProjectile, PulseWaveProjectile
)


class Boss6(Enemy):
    """Sixieme Boss - Le Vortex du Neant avec des patterns gravitationnels"""
    def __init__(self, x, y, speed=2, target_y=80):
        self.size = 200
        self.hp = 70
        self.max_hp = 70
        self.speed = speed
        self.target_y = target_y
        self.timer = 0
        self.shoot_timer = 0
        self.shoot_delay_frames = 20
        self.shoot_count = 0
        self.pattern = 0
        self.pattern_timer = 0
        self.pattern_duration = 300
        self.is_dying = False
        self.death_timer = 0
        self.death_explosions = []

        self.distortion_angle = 0
        self.distortion_amplitude = 30

        self.black_hole_active = False
        self.black_hole_timer = 0
        self.black_hole_duration = 120
        self.black_hole_cooldown = 0

        self.fury_mode = False

        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.create_sprite()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.rotation_angle = 0

    def create_sprite(self):
        """Cree un sprite de vortex/spirale noir et violet"""
        center = self.size // 2

        for r in range(center, 0, -2):
            progress = r / center
            color_val = int(50 * progress)
            alpha = int(200 * progress)
            pygame.draw.circle(self.base_image, (color_val, 0, color_val + 30, alpha),
                             (center, center), r)

        for arm in range(6):
            base_angle = arm * (math.pi / 3)
            for i in range(50):
                t = i / 50
                spiral_r = 20 + t * (center - 30)
                angle = base_angle + t * 4 * math.pi
                x = center + int(math.cos(angle) * spiral_r)
                y = center + int(math.sin(angle) * spiral_r)
                size = max(2, int(6 * (1 - t)))
                color = (150 + int(50 * t), 0, 200, int(255 * (1 - t * 0.5)))
                if 0 <= x < self.size and 0 <= y < self.size:
                    pygame.draw.circle(self.base_image, color, (x, y), size)

        pygame.draw.circle(self.base_image, (100, 0, 150), (center, center), 25)
        pygame.draw.circle(self.base_image, (50, 0, 80), (center, center), 18)
        pygame.draw.circle(self.base_image, (0, 0, 0), (center, center), 10)

    def take_damage(self, damage):
        if not self.black_hole_active:
            self.hp -= damage
            if self.hp <= self.max_hp * 0.25 and not self.fury_mode:
                self.fury_mode = True
                self.shoot_delay_frames = 6
                print("Boss 6 entre en mode FUREUR!")

    def update(self, player_pos, projectiles_list):
        if self.is_dying:
            return self.update_death()

        self.timer += 1
        self.pattern_timer += 1
        self.distortion_angle += 0.05
        self.rotation_angle += 2 if not self.fury_mode else 4

        if self.rect.centery < self.target_y:
            self.rect.y += self.speed
        else:
            offset_x = math.sin(self.distortion_angle) * self.distortion_amplitude
            offset_y = math.cos(self.distortion_angle * 0.7) * (self.distortion_amplitude * 0.5)
            base_x = SCREEN_WIDTH // 2 + offset_x

            self.rect.centerx = int(base_x)
            self.rect.centery = int(self.target_y + offset_y)

        if self.black_hole_cooldown > 0:
            self.black_hole_cooldown -= 1

        if self.black_hole_active:
            self.black_hole_timer += 1
            if self.black_hole_timer >= self.black_hole_duration:
                self.black_hole_active = False
                self.black_hole_timer = 0
                self.black_hole_cooldown = 300

        if self.pattern_timer >= self.pattern_duration:
            self.pattern_timer = 0
            if self.fury_mode:
                self.pattern = random.randint(0, 8)
            else:
                self.pattern = (self.pattern + 1) % 7

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay_frames and self.rect.centery >= self.target_y:
            self.shoot_timer = 0
            self.shoot(player_pos, projectiles_list)

        self.image = pygame.transform.rotate(self.base_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        return False

    def shoot(self, player_pos, projectiles_list):
        cx, cy = self.rect.center
        self.shoot_count += 1

        if self.pattern == 0:
            for i in range(2):
                angle = (i / 2) * 2 * math.pi + self.timer * 0.08
                spawn_x = cx + math.cos(angle) * 60
                spawn_y = cy + math.sin(angle) * 60
                proj = VortexProjectile(spawn_x, spawn_y, player_pos[0], player_pos[1])
                projectiles_list.append(proj)

        elif self.pattern == 1:
            if self.shoot_count % 3 == 1:
                proj = PulseWaveProjectile(cx, cy, speed=4)
                projectiles_list.append(proj)

        elif self.pattern == 2:
            if self.shoot_count % 2 == 1:
                for i in range(3):
                    x = cx - 80 + i * 80
                    proj = MirrorProjectile(x, cy + 40, 0, 1, speed=4)
                    projectiles_list.append(proj)

        elif self.pattern == 3:
            angle = self.timer * 0.15
            for offset in [0, math.pi]:
                spawn_x = cx + math.cos(angle + offset) * 100
                spawn_y = cy + math.sin(angle + offset) * 100
                dx = -math.cos(angle + offset)
                dy = -math.sin(angle + offset) + 0.5
                proj = Boss6Projectile(spawn_x, spawn_y, dx, dy, speed=3)
                projectiles_list.append(proj)

        elif self.pattern == 4:
            if not self.black_hole_active and self.black_hole_cooldown == 0:
                self.black_hole_active = True
                self.black_hole_timer = 0
                proj = BlackHoleProjectile(cx, cy + 150, lifetime=self.black_hole_duration)
                projectiles_list.append(proj)
            for i in range(6):
                angle = (i / 6) * 2 * math.pi
                dx = math.cos(angle)
                dy = math.sin(angle)
                proj = Boss6Projectile(cx, cy, dx, dy, speed=4)
                projectiles_list.append(proj)

        elif self.pattern == 5:
            if self.shoot_count % 2 == 0:
                for i in range(12):
                    x = (i / 11) * SCREEN_WIDTH
                    wave_offset = math.sin(i * 0.5 + self.timer * 0.1) * 30
                    proj = Boss6Projectile(x, cy + 50 + wave_offset, 0, 1, speed=3)
                    projectiles_list.append(proj)

        elif self.pattern == 6:
            side = 1 if self.shoot_count % 2 == 0 else -1
            start_x = cx + side * 80
            dx = -side * 0.3
            dy = 1
            proj = Boss6Projectile(start_x, cy + 30, dx, dy, speed=5)
            projectiles_list.append(proj)

        if self.fury_mode:
            if self.pattern == 7:
                for side in [-1, 1]:
                    for i in range(3):
                        angle = (i / 3) * 2 * math.pi + self.timer * 0.1
                        spawn_x = cx + side * 60 + math.cos(angle) * 40
                        spawn_y = cy + math.sin(angle) * 40
                        proj = VortexProjectile(spawn_x, spawn_y,
                                               player_pos[0], player_pos[1])
                        projectiles_list.append(proj)

            elif self.pattern == 8:
                if self.shoot_count % 2 == 0:
                    projectiles_list.append(PulseWaveProjectile(cx, cy, speed=5))
                angle = self.timer * 0.2
                for offset in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    dx = math.cos(angle + offset)
                    dy = math.sin(angle + offset) * 0.5 + 0.5
                    proj = Boss6Projectile(cx, cy, dx, dy, speed=4)
                    projectiles_list.append(proj)

    def update_death(self):
        self.death_timer += 1

        if self.death_timer % 6 == 0:
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
                                                    self.rotation_angle + self.death_timer * 5,
                                                    shrink)
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.death_timer >= 150:
            return True
        return False

    def draw(self, surface):
        if self.black_hole_active:
            pulse = abs(math.sin(self.timer * 0.15)) * 20
            aura_surf = pygame.Surface((self.size + 60, self.size + 60), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (100, 0, 150, 100),
                             (self.size//2 + 30, self.size//2 + 30),
                             int(self.size//2 + 20 + pulse))
            surface.blit(aura_surf, (self.rect.centerx - self.size//2 - 30,
                                     self.rect.centery - self.size//2 - 30))

        surface.blit(self.image, self.rect)

        if self.fury_mode:
            fury_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.15)))
            fury_surf = pygame.Surface((120, 25), pygame.SRCALPHA)
            pygame.draw.rect(fury_surf, (100, 0, 150, fury_alpha), (0, 0, 120, 25))
            surface.blit(fury_surf, (self.rect.centerx - 60, self.rect.top - 35))

        for exp in self.death_explosions:
            exp.draw(surface)
