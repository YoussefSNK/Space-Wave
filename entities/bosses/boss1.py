import pygame
import random
import math

from config import SCREEN_WIDTH, BLACK
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import BossProjectile
from resource_path import resource_path


class Boss(Enemy):
    def __init__(self, x, y, speed=2, target_y=150):
        super().__init__(x, y, speed)

        self.sprite_normal = pygame.image.load(resource_path("sprites/Miedd.png")).convert_alpha()
        self.sprite_normal = pygame.transform.scale(self.sprite_normal, (100, 100))
        self.sprite_shoot_1 = pygame.image.load(resource_path("sprites/Miedd_shoot_1.png")).convert_alpha()
        self.sprite_shoot_1 = pygame.transform.scale(self.sprite_shoot_1, (100, 100))
        self.sprite_shoot_2 = pygame.image.load(resource_path("sprites/Miedd_shoot_2.png")).convert_alpha()
        self.sprite_shoot_2 = pygame.transform.scale(self.sprite_shoot_2, (100, 100))
        self.sprite_damaged_1 = pygame.image.load(resource_path("sprites/Miedd_damaged.png")).convert_alpha()
        self.sprite_damaged_1 = pygame.transform.scale(self.sprite_damaged_1, (100, 100))
        self.sprite_damaged_2 = pygame.image.load(resource_path("sprites/Miedd_damaged_2.png")).convert_alpha()
        self.sprite_damaged_2 = pygame.transform.scale(self.sprite_damaged_2, (100, 100))

        self.image = self.sprite_normal
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 20
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 20
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 300
        self.lateral_movement_speed = 2
        self.lateral_direction = 1

        self.shoot_animation_frames = [self.sprite_shoot_1, self.sprite_shoot_2, self.sprite_shoot_1, self.sprite_normal]
        self.current_animation_frame = 0
        self.animation_active = False
        self.frames_per_animation_step = 3
        self.animation_timer = 0

        self.damage_animation_active = False
        self.damage_animation_duration = 20
        self.damage_animation_timer = 0
        self.damage_flash_interval = 5

        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 180
        self.death_explosion_timer = 0
        self.death_explosion_interval = 10
        self.death_explosions = []

        self.eye_left_center = (32, 35)
        self.eye_left_radius_x = 11
        self.eye_left_radius_y = 9
        self.pupil_left_offset = (0, 0)

        self.eye_right_center = (69, 36)
        self.eye_right_radius_x = 13
        self.eye_right_radius_y = 10
        self.pupil_right_offset = (0, 0)

    def update(self, player_position=None, enemy_projectiles=None, player_position2=None):
        self.timer += 1

        if self.is_dying:
            self.death_animation_timer += 1

            progress = self.death_animation_timer / self.death_animation_duration
            current_flash_interval = max(2, int(10 * (1 - progress * 0.8)))

            frame_in_cycle = (self.death_animation_timer // current_flash_interval) % 2
            if frame_in_cycle == 0:
                self.image = self.sprite_damaged_1
            else:
                self.image = self.sprite_damaged_2

            self.death_explosion_timer += 1
            explosion_interval = max(3, int(15 * (1 - progress * 0.7)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(10, 90)
                rand_y = self.rect.top + random.randint(10, 90)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=400))

            for exp in self.death_explosions:
                exp.update()
            self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

            if self.death_animation_timer >= self.death_animation_duration:
                return True
            return False

        if self.damage_animation_active:
            self.damage_animation_timer += 1
            frame_in_cycle = (self.damage_animation_timer // self.damage_flash_interval) % 2
            if frame_in_cycle == 0:
                self.image = self.sprite_damaged_1
            else:
                self.image = self.sprite_damaged_2

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self.sprite_normal

        elif self.animation_active:
            self.animation_timer += 1
            if self.animation_timer >= self.frames_per_animation_step:
                self.animation_timer = 0
                self.current_animation_frame += 1
                if self.current_animation_frame >= len(self.shoot_animation_frames):
                    self.animation_active = False
                    self.current_animation_frame = 0
                    self.image = self.sprite_normal
                else:
                    self.image = self.shoot_animation_frames[self.current_animation_frame]

        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss en position de combat!")
        else:
            self.rect.x += self.lateral_direction * self.lateral_movement_speed
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.lateral_direction *= -1

            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 4
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

                    self.animation_active = True
                    self.current_animation_frame = 0
                    self.animation_timer = 0
                    self.image = self.shoot_animation_frames[0]

        # Déterminer les positions pour chaque œil
        # Si player_position2 est None ou si player_position est None, utiliser la position disponible pour les deux yeux
        left_eye_target = player_position
        right_eye_target = player_position2 if player_position2 else player_position

        # Si player_position est None mais player_position2 existe, utiliser player_position2 pour les deux
        if not left_eye_target and right_eye_target:
            left_eye_target = right_eye_target

        # Mise à jour de l'œil gauche
        if left_eye_target:
            px, py = left_eye_target
            eye_left_world_x = self.rect.left + self.eye_left_center[0]
            eye_left_world_y = self.rect.top + self.eye_left_center[1]
            dx_left = px - eye_left_world_x
            dy_left = py - eye_left_world_y
            dist_left = math.sqrt(dx_left**2 + dy_left**2)

            if dist_left > 0:
                dx_left /= dist_left
                dy_left /= dist_left
                max_offset_x_left = self.eye_left_radius_x - 3
                max_offset_y_left = self.eye_left_radius_y - 3
                self.pupil_left_offset = (dx_left * max_offset_x_left, dy_left * max_offset_y_left)

        # Mise à jour de l'œil droit
        if right_eye_target:
            px, py = right_eye_target
            eye_right_world_x = self.rect.left + self.eye_right_center[0]
            eye_right_world_y = self.rect.top + self.eye_right_center[1]
            dx_right = px - eye_right_world_x
            dy_right = py - eye_right_world_y
            dist_right = math.sqrt(dx_right**2 + dy_right**2)

            if dist_right > 0:
                dx_right /= dist_right
                dy_right /= dist_right
                max_offset_x_right = self.eye_right_radius_x - 3
                max_offset_y_right = self.eye_right_radius_y - 3
                self.pupil_right_offset = (dx_right * max_offset_x_right, dy_right * max_offset_y_right)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles selon le pattern"""
        projectiles = []
        bx = self.rect.left + 51
        by = self.rect.top + 72

        if pattern_index == 0:
            projectiles.append(self._create_aimed_projectile(player_position))
            print("Boss: Tir direct!")

        elif pattern_index == 1:
            angles = [-30, -15, 0, 15, 30]
            for angle_deg in angles:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(BossProjectile(bx, by, dx, dy, speed=6))
            print("Boss: Tir en eventail!")

        elif pattern_index == 2:
            num_projectiles = 8
            for i in range(num_projectiles):
                angle = (2 * math.pi / num_projectiles) * i
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(BossProjectile(bx, by, dx, dy, speed=5))
            print("Boss: Tir circulaire!")

        elif pattern_index == 3:
            offsets = [(-20, 0), (0, 0), (20, 0)]
            for offset_x, offset_y in offsets:
                proj = self._create_aimed_projectile(player_position, offset_x, offset_y)
                projectiles.append(proj)
            print("Boss: Triple tir!")

        return projectiles

    def _create_aimed_projectile(self, player_position, offset_x=0, offset_y=0):
        """Cree un projectile visant le joueur"""
        bx = self.rect.left + 51 + offset_x
        by = self.rect.top + 72 + offset_y
        px, py = player_position
        dx = px - bx
        dy = py - by
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            dist = 1
        dx /= dist
        dy /= dist
        return BossProjectile(bx, by, dx, dy, speed=7)

    def take_damage(self, amount=1):
        """Applique des degats au boss et declenche l'animation"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        if not self.is_dying:
            cross_size = 1

            pupil_left_x = self.rect.left + self.eye_left_center[0] + int(self.pupil_left_offset[0])
            pupil_left_y = self.rect.top + self.eye_left_center[1] + int(self.pupil_left_offset[1])
            pygame.draw.line(surface, BLACK,
                            (pupil_left_x - cross_size, pupil_left_y),
                            (pupil_left_x + cross_size, pupil_left_y), 1)
            pygame.draw.line(surface, BLACK,
                            (pupil_left_x, pupil_left_y - cross_size),
                            (pupil_left_x, pupil_left_y + cross_size), 1)

            pupil_right_x = self.rect.left + self.eye_right_center[0] + int(self.pupil_right_offset[0])
            pupil_right_y = self.rect.top + self.eye_right_center[1] + int(self.pupil_right_offset[1])
            pygame.draw.line(surface, BLACK,
                            (pupil_right_x - cross_size, pupil_right_y),
                            (pupil_right_x + cross_size, pupil_right_y), 1)
            pygame.draw.line(surface, BLACK,
                            (pupil_right_x, pupil_right_y - cross_size),
                            (pupil_right_x, pupil_right_y + cross_size), 1)

        for exp in self.death_explosions:
            exp.draw(surface)
