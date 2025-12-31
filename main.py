import pygame
import random
import math

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 1000
FPS = 60

BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
YELLOW  = (255, 255, 0)
WHITE   = (255, 255, 255)
CYAN    = (0, 255, 255)
ORANGE  = (255, 165, 0)

class ComboSystem:
    """Système de combo - se termine après 5s d'inactivité ou si un tir rate"""
    def __init__(self):
        self.count = 0
        self.last_hit_time = 0
        self.timeout = 5000  # 5 secondes en millisecondes
        self.active = False

    def hit(self):
        """Appelé quand le joueur touche un ennemi"""
        now = pygame.time.get_ticks()
        if not self.active:
            self.active = True
            self.count = 1
        else:
            self.count += 1
        self.last_hit_time = now

    def miss(self):
        """Appelé quand un tir quitte l'écran sans toucher - reset le combo"""
        if self.active:
            print(f"Combo perdu ! (tir raté) - Score final: {self.count}")
        self.reset()

    def reset(self):
        """Remet le combo à zéro"""
        self.count = 0
        self.active = False
        self.last_hit_time = 0

    def update(self):
        """Met à jour le combo - vérifie le timeout"""
        if self.active:
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.timeout:
                print(f"Combo expiré ! (timeout) - Score final: {self.count}")
                self.reset()

    def draw(self, surface, font):
        """Affiche le combo en haut à droite"""
        if self.active and self.count > 0:
            combo_text = font.render(f"COMBO x{self.count}", True, YELLOW)
            text_rect = combo_text.get_rect()
            text_rect.topright = (SCREEN_WIDTH - 10, 10)
            surface.blit(combo_text, text_rect)


class Background:
    def __init__(self, image_path=None, speed=2):
        self.speed = speed
        self.default_speed = speed
        if image_path:
            self.image = pygame.image.load(image_path).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((10, 10, 30))
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.image, WHITE, (x, y), 1)
        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))


class Explosion:
    def __init__(self, x, y, duration=300):
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.max_radius = 30

        self.particles = []
        num_particles = random.randint(8, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': random.randint(2, 6),
                'color': random.choice([
                    (255, 100, 0),   # Orange
                    (255, 150, 0),   # Orange clair
                    (255, 200, 50),  # Jaune-orange
                    (255, 50, 0),    # Rouge-orange
                ])
            }
            self.particles.append(particle)

    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            p['radius'] = max(0, p['radius'] - 0.1)

    def draw(self, surface):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            return
        progress = elapsed / self.duration

        if progress < 0.3:
            radius = int(self.max_radius * (progress / 0.3))
        else:
            radius = int(self.max_radius * (1 - (progress - 0.3) / 0.7))

        if radius < 1:
            radius = 1
        alpha = int(255 * (1 - progress))

        size = radius * 2 + 20
        explosion_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        if radius > 5:
            outer_alpha = int(alpha * 0.3)
            pygame.draw.circle(explosion_surf, (100, 30, 0, outer_alpha), (center, center), radius + 5)

        if radius > 3:
            mid_alpha = int(alpha * 0.6)
            pygame.draw.circle(explosion_surf, (255, 100, 0, mid_alpha), (center, center), int(radius * 0.8))

        if radius > 2:
            inner_alpha = int(alpha * 0.9)
            pygame.draw.circle(explosion_surf, (255, 200, 50, inner_alpha), (center, center), int(radius * 0.5))

        if progress < 0.2 and radius > 1:
            flash_alpha = int(255 * (1 - progress / 0.2))
            pygame.draw.circle(explosion_surf, (255, 255, 255, flash_alpha), (center, center), int(radius * 0.3))

        surface.blit(explosion_surf, (self.x - center, self.y - center))

        for p in self.particles:
            if p['radius'] > 0:
                particle_alpha = int(alpha * 0.8)
                color_with_alpha = (*p['color'], particle_alpha)
                particle_surf = pygame.Surface((int(p['radius']*2), int(p['radius']*2)), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color_with_alpha, (int(p['radius']), int(p['radius'])), int(p['radius']))
                surface.blit(particle_surf, (int(p['x'] - p['radius']), int(p['y'] - p['radius'])))

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time > self.duration


class PowerUp:
    """Power-up qui tombe et améliore les tirs du joueur"""
    def __init__(self, x, y, power_type='double'):
        self.power_type = power_type
        self.image = pygame.Surface((30, 30))

        if power_type == 'double':
            self.color = CYAN
        elif power_type == 'triple':
            self.color = (255, 0, 255)
        elif power_type == 'spread':
            self.color = (0, 255, 100)
        else:
            self.color = WHITE

        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.angle = 0

    def update(self):
        self.rect.y += self.speed
        self.angle += 5

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)

        pulse = abs(math.sin(self.angle * 0.1)) * 10 + 5
        pygame.draw.circle(surface, self.color, self.rect.center, int(20 + pulse), 2)

        surface.blit(rotated, new_rect)


class MovementPattern:
    """Classe de base pour les patterns de mouvement"""
    def update(self, enemy):
        pass


class SineWavePattern(MovementPattern):
    """Mouvement sinusoïdal (vague)"""
    def __init__(self, amplitude=100, frequency=0.05, base_speed=3):
        self.amplitude = amplitude
        self.frequency = frequency
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        offset_x = math.sin(enemy.timer * self.frequency) * self.amplitude
        enemy.rect.x = enemy.start_x + offset_x


class ZigZagPattern(MovementPattern):
    """Mouvement en zigzag"""
    def __init__(self, amplitude=80, switch_time=30, base_speed=3):
        self.amplitude = amplitude
        self.switch_time = switch_time
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        direction = 1 if (enemy.timer // self.switch_time) % 2 == 0 else -1
        enemy.rect.x += direction * 3


class CirclePattern(MovementPattern):
    """Mouvement circulaire"""
    def __init__(self, radius=60, angular_speed=0.08, base_speed=2):
        self.radius = radius
        self.angular_speed = angular_speed
        self.base_speed = base_speed

    def update(self, enemy):
        enemy.rect.y += self.base_speed
        angle = enemy.timer * self.angular_speed
        offset_x = math.cos(angle) * self.radius
        offset_y = math.sin(angle) * self.radius
        enemy.rect.x = enemy.start_x + offset_x
        enemy.rect.centery = enemy.start_y + (enemy.timer * self.base_speed) + offset_y


class SwoopPattern(MovementPattern):
    """Mouvement en piqué puis remontée latérale"""
    def __init__(self, swoop_direction=1):
        self.swoop_direction = swoop_direction  # 1 pour droite, -1 pour gauche
        self.phase = 0

    def update(self, enemy):
        if enemy.timer < 60: 
            enemy.rect.y += 5
        elif enemy.timer < 120:
            enemy.rect.y += 2
            enemy.rect.x += self.swoop_direction * 4
        else:
            enemy.rect.y -= 1
            enemy.rect.x += self.swoop_direction * 3


class HorizontalWavePattern(MovementPattern):
    """Se déplace horizontalement avec légère descente"""
    def __init__(self, direction=1, speed=4):
        self.direction = direction
        self.speed = speed

    def update(self, enemy):
        enemy.rect.x += self.direction * self.speed
        enemy.rect.y += 1
        if enemy.rect.left <= 0 or enemy.rect.right >= SCREEN_WIDTH:
            self.direction *= -1


class Enemy:
    def __init__(self, x, y, speed=3, movement_pattern=None):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hp = 2
        self.movement_pattern = movement_pattern
        self.timer = 0
        self.start_x = x
        self.start_y = y
        self.drops_powerup = False

    def update(self):
        self.timer += 1
        if self.movement_pattern:
            self.movement_pattern.update(self)
        else:
            self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Boss(Enemy):
    def __init__(self, x, y, speed=2, target_y=150):
        super().__init__(x, y, speed)

        self.sprite_normal = pygame.image.load("sprites/Miedd.png").convert_alpha()
        self.sprite_normal = pygame.transform.scale(self.sprite_normal, (100, 100))
        self.sprite_shoot_1 = pygame.image.load("sprites/Miedd_shoot_1.png").convert_alpha()
        self.sprite_shoot_1 = pygame.transform.scale(self.sprite_shoot_1, (100, 100))
        self.sprite_shoot_2 = pygame.image.load("sprites/Miedd_shoot_2.png").convert_alpha()
        self.sprite_shoot_2 = pygame.transform.scale(self.sprite_shoot_2, (100, 100))
        self.sprite_damaged_1 = pygame.image.load("sprites/Miedd_damaged.png").convert_alpha()
        self.sprite_damaged_1 = pygame.transform.scale(self.sprite_damaged_1, (100, 100))
        self.sprite_damaged_2 = pygame.image.load("sprites/Miedd_damaged_2.png").convert_alpha()
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

    def update(self, player_position=None, enemy_projectiles=None):
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

        # animation de dégâts (priorité sur l'animation de tir)
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

        # calcul offset yeux qui suivent J1
        if player_position:
            px, py = player_position

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
            print("Boss: Tir en éventail!")

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
        """Crée un projectile visant le joueur"""
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
        """Applique des dégâts au boss et déclenche l'animation"""
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


class ShootingEnemy(Enemy):
    def __init__(self, x, y, speed=3, shoot_delay_frames=60):
        super().__init__(x, y, speed)
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 0, 200))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.shoot_delay_frames = shoot_delay_frames
        self.last_shot_frame = 0

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        if self.timer < 120:
            self.rect.y += self.speed
        else:
            if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                self.last_shot_frame = self.timer
                proj = self.shoot(player_position)
                enemy_projectiles.append(proj)

    def shoot(self, player_position):
        ex, ey = self.rect.center
        px, py = player_position
        dx = px - ex
        dy = py - ey
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            dist = 1
        dx /= dist
        dy /= dist
        return EnemyProjectile(ex, ey, dx, dy, speed=7)

class EnemyProjectile:
    def __init__(self, x, y, dx, dy, speed=7):
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.trail = []
        self.max_trail_length = 5

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(1, int(3 * progress))
            color = (RED[0], RED[1], RED[2], alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        surface.blit(self.image, self.rect)


class BossProjectile(EnemyProjectile):
    """Projectiles du Boss - Plus gros et plus visibles"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((15, 15))  # 3x plus gros
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 8

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, int(100 + 65 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, ORANGE, self.rect.center, 7)
        pygame.draw.circle(surface, RED, self.rect.center, 5)
        pygame.draw.circle(surface, YELLOW, self.rect.center, 2)


class Boss2Projectile(EnemyProjectile):
    """Projectiles du Boss 2 - Violets et menaçants"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((15, 15))
        self.image.fill((150, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (150, 0, int(255 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (150, 0, 255), self.rect.center, 7)
        pygame.draw.circle(surface, (200, 50, 255), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class Boss2(Enemy):
    """Second Boss - Plus agressif avec des patterns différents"""
    def __init__(self, x, y, speed=2, target_y=120):
        super().__init__(x, y, speed)

        # Créer un sprite procédural pour le Boss 2 (forme de crâne/démon)
        self.size = 120
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 30  # Plus de HP que le premier boss
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 15  # Tire plus vite
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 240  # Change de pattern plus souvent
        self.lateral_movement_speed = 3  # Plus rapide latéralement
        self.lateral_direction = 1

        # Animation de dégâts
        self.damage_animation_active = False
        self.damage_animation_duration = 20
        self.damage_animation_timer = 0
        self.damage_flash_interval = 4

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 200
        self.death_explosion_timer = 0
        self.death_explosion_interval = 8
        self.death_explosions = []

        # Variables pour les patterns spéciaux
        self.spiral_angle = 0
        self.laser_charging = False
        self.laser_charge_timer = 0
        self.laser_active = False
        self.laser_duration = 60
        self.laser_timer = 0

        # Pulsation visuelle
        self.pulse_timer = 0

    def _create_boss_sprite(self):
        """Crée un sprite procédural pour le Boss 2"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Corps principal - forme hexagonale menaçante
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 90)
            radius = 50
            x = center + math.cos(angle) * radius
            y = center + math.sin(angle) * radius
            points.append((x, y))
        pygame.draw.polygon(surf, (80, 0, 120), points)
        pygame.draw.polygon(surf, (150, 0, 200), points, 3)

        # Yeux rouges menaçants
        pygame.draw.circle(surf, (255, 0, 0), (center - 20, center - 10), 12)
        pygame.draw.circle(surf, (255, 0, 0), (center + 20, center - 10), 12)
        pygame.draw.circle(surf, (255, 255, 0), (center - 20, center - 10), 6)
        pygame.draw.circle(surf, (255, 255, 0), (center + 20, center - 10), 6)

        # "Bouche" - ligne menaçante
        pygame.draw.line(surf, (255, 0, 0), (center - 25, center + 20), (center + 25, center + 20), 3)

        return surf

    def _create_damaged_sprite(self):
        """Crée un sprite endommagé"""
        surf = self._create_boss_sprite()
        # Ajouter un effet de flash blanc
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

            # Flash rapide
            if (self.death_animation_timer // 3) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_boss_sprite()

            # Explosions de plus en plus fréquentes
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

        # Animation de dégâts
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

        # Déplacement vers la position
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 2 en position de combat!")
        else:
            # Mouvement latéral plus agressif
            self.rect.x += self.lateral_direction * self.lateral_movement_speed
            if self.rect.left <= 50 or self.rect.right >= SCREEN_WIDTH - 50:
                self.lateral_direction *= -1

            # Tir
            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 5
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles selon le pattern - patterns différents du Boss 1"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 10

        if pattern_index == 0:
            # Pattern 0: Tir en spirale
            self.spiral_angle += 30
            for i in range(3):
                angle = math.radians(self.spiral_angle + i * 120)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=5))
            print("Boss 2: Tir spiral!")

        elif pattern_index == 1:
            # Pattern 1: Pluie de projectiles (vertical)
            for i in range(5):
                offset_x = (i - 2) * 40
                projectiles.append(Boss2Projectile(bx + offset_x, by, 0, 1, speed=8))
            print("Boss 2: Pluie de feu!")

        elif pattern_index == 2:
            # Pattern 2: Double vague (deux arcs opposés)
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
            # Pattern 3: Croix rotative
            cross_angle = (self.timer * 3) % 360
            for i in range(4):
                angle = math.radians(cross_angle + i * 90)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=6))
            print("Boss 2: Croix rotative!")

        elif pattern_index == 4:
            # Pattern 4: Tir ciblé en rafale (3 tirs rapides vers le joueur)
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            # Tir principal + 2 tirs légèrement décalés
            projectiles.append(Boss2Projectile(bx, by, dx, dy, speed=9))
            # Tirs avec léger décalage angulaire
            for offset in [-10, 10]:
                angle = math.atan2(dy, dx) + math.radians(offset)
                ndx = math.cos(angle)
                ndy = math.sin(angle)
                projectiles.append(Boss2Projectile(bx, by, ndx, ndy, speed=8))
            print("Boss 2: Rafale ciblée!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des dégâts au boss et déclenche l'animation"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        # Effet de pulsation
        pulse = abs(math.sin(self.pulse_timer * 0.05)) * 0.2 + 0.8

        if not self.is_dying:
            # Aura violette
            aura_size = int(70 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (100, 0, 150, 50), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)


class Boss3Projectile(EnemyProjectile):
    """Projectiles du Boss 3 - Cyan/électriques"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 12

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (0, int(200 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, CYAN, self.rect.center, 6)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class HomingProjectile(EnemyProjectile):
    """Projectile à tête chercheuse pour le Boss 3"""
    def __init__(self, x, y, speed=4):
        super().__init__(x, y, 0, 1, speed)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 15
        self.lifetime = 180  # 3 secondes max
        self.timer = 0
        self.turn_speed = 0.05

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(5 * progress))
            color = (255, int(100 * progress), int(100 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self, player_position=None):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Poursuite du joueur
        if player_position and self.timer < self.lifetime:
            px, py = player_position
            target_dx = px - self.rect.centerx
            target_dy = py - self.rect.centery
            dist = math.sqrt(target_dx**2 + target_dy**2)
            if dist > 0:
                target_dx /= dist
                target_dy /= dist
                # Interpolation vers la cible
                self.dx += (target_dx - self.dx) * self.turn_speed
                self.dy += (target_dy - self.dy) * self.turn_speed
                # Renormaliser
                d = math.sqrt(self.dx**2 + self.dy**2)
                if d > 0:
                    self.dx /= d
                    self.dy /= d

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 100, 100), self.rect.center, 5)
        pygame.draw.circle(surface, (255, 200, 200), self.rect.center, 2)


class Boss3(Enemy):
    """Troisième Boss - Le plus difficile avec des patterns complexes"""
    def __init__(self, x, y, speed=2, target_y=100):
        super().__init__(x, y, speed)

        self.size = 140
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 40  # Encore plus de HP
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 12  # Tire encore plus vite
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 200  # Change de pattern très souvent
        self.lateral_movement_speed = 2
        self.lateral_direction = 1

        # Mouvement sinusoïdal vertical
        self.vertical_amplitude = 30
        self.vertical_frequency = 0.02

        # Animation de dégâts
        self.damage_animation_active = False
        self.damage_animation_duration = 15
        self.damage_animation_timer = 0
        self.damage_flash_interval = 3

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 240
        self.death_explosion_timer = 0
        self.death_explosions = []

        # Variables pour les patterns spéciaux
        self.wave_angle = 0
        self.laser_warning_timer = 0
        self.laser_warning_duration = 60
        self.laser_active = False
        self.laser_timer = 0
        self.laser_duration = 90
        self.laser_target_x = 0

        # Téléportation
        self.teleport_cooldown = 300
        self.last_teleport = -300

        # Pulsation visuelle
        self.pulse_timer = 0
        self.core_rotation = 0

    def _create_boss_sprite(self):
        """Crée un sprite procédural pour le Boss 3 - forme de diamant/cristal"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Corps principal - forme de diamant
        diamond_points = [
            (center, 10),           # Haut
            (center + 55, center),  # Droite
            (center, self.size - 10),  # Bas
            (center - 55, center),  # Gauche
        ]
        pygame.draw.polygon(surf, (0, 80, 100), diamond_points)
        pygame.draw.polygon(surf, (0, 200, 255), diamond_points, 4)

        # Lignes internes
        pygame.draw.line(surf, (0, 150, 200), (center, 10), (center, self.size - 10), 2)
        pygame.draw.line(surf, (0, 150, 200), (center - 55, center), (center + 55, center), 2)

        # Œil central
        pygame.draw.circle(surf, (0, 255, 255), (center, center), 20)
        pygame.draw.circle(surf, WHITE, (center, center), 12)
        pygame.draw.circle(surf, (0, 100, 150), (center, center), 6)

        # Petits cristaux sur les côtés
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            cx = center + math.cos(rad) * 35
            cy = center + math.sin(rad) * 35
            pygame.draw.circle(surf, (0, 200, 255), (int(cx), int(cy)), 8)
            pygame.draw.circle(surf, WHITE, (int(cx), int(cy)), 4)

        return surf

    def _create_damaged_sprite(self):
        """Crée un sprite endommagé"""
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

        # Animation de dégâts
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

        # Déplacement vers la position
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 3 en position de combat!")
        else:
            # Mouvement latéral + oscillation verticale
            self.rect.x += self.lateral_direction * self.lateral_movement_speed
            if self.rect.left <= 80 or self.rect.right >= SCREEN_WIDTH - 80:
                self.lateral_direction *= -1

            # Oscillation verticale
            vertical_offset = math.sin(self.timer * self.vertical_frequency) * self.vertical_amplitude
            self.rect.centery = self.target_y + int(vertical_offset)

            # Gestion du laser
            if self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active = True
                    self.laser_timer = self.laser_duration

            if self.laser_active:
                self.laser_timer -= 1
                if self.laser_timer <= 0:
                    self.laser_active = False

            # Tir
            if player_position and enemy_projectiles is not None and not self.laser_active:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 6
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns uniques au Boss 3"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 20

        if pattern_index == 0:
            # Pattern 0: Vague sinusoïdale de projectiles
            self.wave_angle += 15
            for i in range(7):
                offset = (i - 3) * 25
                angle = math.radians(self.wave_angle + i * 20)
                dy = 1
                dx = math.sin(angle) * 0.3
                projectiles.append(Boss3Projectile(bx + offset, by, dx, dy, speed=6))
            print("Boss 3: Vague sinusoïdale!")

        elif pattern_index == 1:
            # Pattern 1: Tirs en X
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
            # Pattern 2: Missiles à tête chercheuse
            projectiles.append(HomingProjectile(bx - 40, by, speed=3))
            projectiles.append(HomingProjectile(bx + 40, by, speed=3))
            print("Boss 3: Missiles guidés!")

        elif pattern_index == 3:
            # Pattern 3: Mur de projectiles avec trou
            hole_position = random.randint(1, 5)
            for i in range(7):
                if i != hole_position and i != hole_position - 1:
                    offset_x = (i - 3) * 60
                    projectiles.append(Boss3Projectile(bx + offset_x, by, 0, 1, speed=5))
            print("Boss 3: Mur avec trou!")

        elif pattern_index == 4:
            # Pattern 4: Explosion radiale en deux temps
            num_projectiles = 12
            for i in range(num_projectiles):
                angle = (2 * math.pi / num_projectiles) * i
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss3Projectile(bx, by, dx, dy, speed=4))
            print("Boss 3: Explosion radiale!")

        elif pattern_index == 5:
            # Pattern 5: Préparer le laser (avertissement)
            if self.laser_warning_timer == 0 and not self.laser_active:
                self.laser_warning_timer = self.laser_warning_duration
                self.laser_target_x = player_position[0]
                print("Boss 3: Laser en charge!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des dégâts au boss et déclenche l'animation"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        # Effet de pulsation
        pulse = abs(math.sin(self.pulse_timer * 0.03)) * 0.3 + 0.7

        if not self.is_dying:
            # Aura cyan
            aura_size = int(80 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (0, 150, 200, 40), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            # Orbes en rotation autour du boss
            for i in range(4):
                angle = math.radians(self.core_rotation + i * 90)
                orb_x = self.rect.centerx + math.cos(angle) * 70
                orb_y = self.rect.centery + math.sin(angle) * 40
                pygame.draw.circle(surface, (0, 255, 255), (int(orb_x), int(orb_y)), 8)
                pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), 4)

        # Avertissement laser
        if self.laser_warning_timer > 0:
            warning_alpha = int(150 * abs(math.sin(self.laser_warning_timer * 0.3)))
            warning_surf = pygame.Surface((40, SCREEN_HEIGHT), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha))
            surface.blit(warning_surf, (self.laser_target_x - 20, 0))

        # Laser actif
        if self.laser_active:
            laser_width = 60
            laser_surf = pygame.Surface((laser_width, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Dégradé du laser
            for i in range(laser_width // 2):
                alpha = int(200 * (1 - i / (laser_width // 2)))
                pygame.draw.line(laser_surf, (0, 255, 255, alpha),
                               (laser_width // 2 - i, 0), (laser_width // 2 - i, SCREEN_HEIGHT))
                pygame.draw.line(laser_surf, (0, 255, 255, alpha),
                               (laser_width // 2 + i, 0), (laser_width // 2 + i, SCREEN_HEIGHT))
            # Cœur du laser
            pygame.draw.rect(laser_surf, WHITE, (laser_width // 2 - 5, 0, 10, SCREEN_HEIGHT))
            surface.blit(laser_surf, (self.laser_target_x - laser_width // 2, 0))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)


class Boss4Projectile(EnemyProjectile):
    """Projectiles du Boss 4 - Dorés/solaires"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, int(180 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 215, 0), self.rect.center, 7)
        pygame.draw.circle(surface, (255, 255, 100), self.rect.center, 4)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class BouncingProjectile(EnemyProjectile):
    """Projectile qui rebondit sur les bords de l'écran"""
    def __init__(self, x, y, dx, dy, speed=5, bounces=3):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 8
        self.bounces_left = bounces

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (255, int(100 * progress), 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

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
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (255, 100, 0), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 100), self.rect.center, 3)


class SplittingProjectile(EnemyProjectile):
    """Projectile qui se divise après un certain temps"""
    def __init__(self, x, y, dx, dy, speed=4, split_time=40, can_split=True):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((16, 16))
        self.image.fill((200, 150, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 6
        self.timer = 0
        self.split_time = split_time
        self.can_split = can_split
        self.has_split = False

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(8 * progress)) if can_split else max(1, int(4 * progress))
            color = (200, int(150 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

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


class Boss4(Enemy):
    """Quatrième Boss - Boss final ultime avec des patterns complexes"""
    def __init__(self, x, y, speed=2, target_y=80):
        super().__init__(x, y, speed)

        self.size = 160
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 50  # Le plus résistant
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 10  # Très rapide
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 180  # Change très souvent
        self.lateral_movement_speed = 2.5
        self.lateral_direction = 1

        # Mouvement en 8
        self.movement_angle = 0
        self.movement_radius_x = 150
        self.movement_radius_y = 40

        # Animation de dégâts
        self.damage_animation_active = False
        self.damage_animation_duration = 12
        self.damage_animation_timer = 0
        self.damage_flash_interval = 2

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 300
        self.death_explosion_timer = 0
        self.death_explosions = []

        # Variables pour les patterns spéciaux
        self.vortex_angle = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 180
        self.shield_cooldown = 600
        self.last_shield_time = -600

        # Charge attack
        self.charging = False
        self.charge_timer = 0
        self.charge_duration = 120
        self.charge_warning_duration = 60
        self.original_y = 0

        # Pulsation visuelle
        self.pulse_timer = 0
        self.ring_rotation = 0
        self.inner_rotation = 0

    def _create_boss_sprite(self):
        """Crée un sprite procédural pour le Boss 4 - Soleil/Étoile divine"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Rayons externes
        for i in range(12):
            angle = math.radians(30 * i)
            inner_radius = 40
            outer_radius = 70
            x1 = center + math.cos(angle) * inner_radius
            y1 = center + math.sin(angle) * inner_radius
            x2 = center + math.cos(angle) * outer_radius
            y2 = center + math.sin(angle) * outer_radius
            pygame.draw.line(surf, (255, 200, 0), (x1, y1), (x2, y2), 4)

        # Corps principal - cercle doré
        pygame.draw.circle(surf, (180, 120, 0), (center, center), 45)
        pygame.draw.circle(surf, (255, 200, 50), (center, center), 40)
        pygame.draw.circle(surf, (255, 215, 0), (center, center), 45, 3)

        # Motif interne - triangle
        triangle_size = 25
        triangle_points = []
        for i in range(3):
            angle = math.radians(120 * i - 90)
            tx = center + math.cos(angle) * triangle_size
            ty = center + math.sin(angle) * triangle_size
            triangle_points.append((tx, ty))
        pygame.draw.polygon(surf, (200, 100, 0), triangle_points)
        pygame.draw.polygon(surf, (255, 150, 0), triangle_points, 2)

        # Œil central
        pygame.draw.circle(surf, (255, 50, 0), (center, center), 15)
        pygame.draw.circle(surf, (255, 255, 0), (center, center), 10)
        pygame.draw.circle(surf, WHITE, (center, center), 5)

        return surf

    def _create_damaged_sprite(self):
        """Crée un sprite endommagé"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 150))
        surf.blit(flash, (0, 0))
        return surf

    def _create_shield_sprite(self):
        """Crée un sprite avec bouclier"""
        surf = self._create_boss_sprite()
        # Ajouter un anneau de bouclier
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

        # Gestion du bouclier
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

        # Gestion de la charge
        if self.charging:
            self.charge_timer += 1
            if self.charge_timer <= self.charge_warning_duration:
                # Phase d'avertissement - tremblement
                shake = random.randint(-3, 3)
                self.rect.x += shake
            elif self.charge_timer <= self.charge_warning_duration + 30:
                # Charge vers le bas
                self.rect.y += 15
            elif self.charge_timer <= self.charge_duration:
                # Retour en position
                if self.rect.centery > self.original_y:
                    self.rect.y -= 5
                else:
                    self.charging = False
                    self.charge_timer = 0
            return False

        # Déplacement vers la position
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                self.original_y = self.rect.centery
                print("Boss 4 en position de combat!")
        else:
            # Mouvement en forme de 8
            self.movement_angle += 0.02
            offset_x = math.sin(self.movement_angle) * self.movement_radius_x
            offset_y = math.sin(self.movement_angle * 2) * self.movement_radius_y
            self.rect.centerx = SCREEN_WIDTH // 2 + int(offset_x)
            self.rect.centery = self.target_y + int(offset_y)

            # Activer le bouclier périodiquement
            if self.hp < 25 and not self.shield_active and self.timer - self.last_shield_time >= self.shield_cooldown:
                self.shield_active = True
                self.shield_timer = 0
                print("Boss 4: Bouclier activé!")

            # Tir
            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 7
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns ultimes du Boss 4"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 20

        if pattern_index == 0:
            # Pattern 0: Vortex - spirale qui s'élargit
            self.vortex_angle += 25
            for i in range(4):
                angle = math.radians(self.vortex_angle + i * 90)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=4))
            print("Boss 4: Vortex!")

        elif pattern_index == 1:
            # Pattern 1: Projectiles rebondissants
            for angle_deg in [-30, 0, 30]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(BouncingProjectile(bx, by, dx, dy, speed=6, bounces=2))
            print("Boss 4: Tirs rebondissants!")

        elif pattern_index == 2:
            # Pattern 2: Projectiles qui se divisent
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
            # Pattern 3: Pluie solaire - cascade de projectiles
            for i in range(9):
                offset_x = (i - 4) * 45
                delay_factor = abs(i - 4) * 0.1
                dy = 1
                dx = delay_factor * (1 if i > 4 else -1)
                projectiles.append(Boss4Projectile(bx + offset_x, by, dx, dy, speed=7))
            print("Boss 4: Pluie solaire!")

        elif pattern_index == 4:
            # Pattern 4: Double anneau
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
            # Pattern 5: Étoile filante - tirs en étoile
            for i in range(5):
                angle = math.radians(72 * i - 90 + self.timer % 72)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss4Projectile(bx, by, dx, dy, speed=8))
                # Tir secondaire décalé
                angle2 = angle + math.radians(36)
                dx2 = math.cos(angle2)
                dy2 = math.sin(angle2)
                projectiles.append(Boss4Projectile(bx, by, dx2, dy2, speed=5))
            print("Boss 4: Étoile filante!")

        elif pattern_index == 6:
            # Pattern 6: Charge - le boss fonce vers le joueur
            if not self.charging and self.timer % 300 < 10:
                self.charging = True
                self.charge_timer = 0
                self.original_y = self.rect.centery
                print("Boss 4: CHARGE!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des dégâts au boss (bloqué si bouclier actif)"""
        if self.shield_active:
            print("Boss 4: Bouclier absorbe les dégâts!")
            return
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        # Effet de pulsation
        pulse = abs(math.sin(self.pulse_timer * 0.04)) * 0.3 + 0.7

        if not self.is_dying:
            # Aura dorée
            aura_size = int(90 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 200, 0, 30), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            # Anneaux en rotation
            for i in range(3):
                ring_radius = 85 + i * 15
                ring_alpha = 100 - i * 30
                ring_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (255, 215, 0, ring_alpha),
                                 (ring_radius + 5, ring_radius + 5), ring_radius, 2)
                # Rotation
                rotated = pygame.transform.rotate(ring_surf, self.ring_rotation * (i + 1) * 0.5)
                rot_rect = rotated.get_rect(center=(self.rect.centerx, self.rect.centery))
                surface.blit(rotated, rot_rect)

            # Particules orbitantes
            for i in range(6):
                angle = math.radians(self.ring_rotation * 2 + i * 60)
                orb_x = self.rect.centerx + math.cos(angle) * 80
                orb_y = self.rect.centery + math.sin(angle) * 50
                pygame.draw.circle(surface, (255, 200, 0), (int(orb_x), int(orb_y)), 6)
                pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), 3)

        # Avertissement de charge
        if self.charging and self.charge_timer <= self.charge_warning_duration:
            warning_alpha = int(200 * abs(math.sin(self.charge_timer * 0.4)))
            warning_surf = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
            warning_surf.fill((255, 100, 0, warning_alpha))
            surface.blit(warning_surf, (0, self.rect.bottom))

        surface.blit(self.image, self.rect)

        for exp in self.death_explosions:
            exp.draw(surface)


class Boss5Projectile(EnemyProjectile):
    """Projectiles du Boss 5 - Verts toxiques/acides"""
    def __init__(self, x, y, dx, dy, speed=7):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((13, 13))
        self.image.fill((0, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 11

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (0, int(255 * progress), int(100 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (0, 255, 100), self.rect.center, 6)
        pygame.draw.circle(surface, (150, 255, 150), self.rect.center, 3)
        pygame.draw.circle(surface, WHITE, self.rect.center, 1)


class ZigZagProjectile(EnemyProjectile):
    """Projectile qui zigzague horizontalement"""
    def __init__(self, x, y, dy, speed=5, amplitude=50, frequency=0.1):
        super().__init__(x, y, 0, dy, speed)
        self.start_x = x
        self.amplitude = amplitude
        self.frequency = frequency
        self.timer = 0
        self.image = pygame.Surface((10, 10))
        self.image.fill((100, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 10

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(5 * progress))
            color = (100, int(255 * progress), 100, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.y += int(self.dy * self.speed)
        # Mouvement zigzag
        self.rect.x = self.start_x + int(math.sin(self.timer * self.frequency) * self.amplitude)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (100, 255, 100), self.rect.center, 5)
        pygame.draw.circle(surface, WHITE, self.rect.center, 2)


class GravityProjectile(EnemyProjectile):
    """Projectile affecté par la gravité"""
    def __init__(self, x, y, dx, dy, speed=8):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12))
        self.image.fill((200, 100, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 12
        self.gravity = 0.15
        self.vy = dy * speed

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(6 * progress))
            color = (200, int(100 * progress), 255, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.vy += self.gravity
        self.rect.y += int(self.vy)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, (200, 100, 255), self.rect.center, 6)
        pygame.draw.circle(surface, (255, 200, 255), self.rect.center, 3)


class TeleportingProjectile(EnemyProjectile):
    """Projectile qui se téléporte périodiquement"""
    def __init__(self, x, y, dx, dy, speed=4):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((14, 14))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 5
        self.timer = 0
        self.teleport_interval = 30
        self.teleport_distance = 80

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(2, int(7 * progress))
            color = (255, 0, int(255 * progress), alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

        # Téléportation
        if self.timer % self.teleport_interval == 0:
            self.rect.y += self.teleport_distance
            self.trail.clear()

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            if i < len(self.trail_cache):
                trail_surf, size = self.trail_cache[i]
                surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        # Effet de scintillement
        if (self.timer // 3) % 2 == 0:
            pygame.draw.circle(surface, (255, 0, 255), self.rect.center, 7)
        else:
            pygame.draw.circle(surface, (255, 100, 255), self.rect.center, 7)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class Boss5(Enemy):
    """Cinquième Boss - Le Némésis ultime avec des patterns chaotiques"""
    def __init__(self, x, y, speed=2, target_y=90):
        super().__init__(x, y, speed)

        self.size = 180
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 60  # Le plus résistant de tous
        self.max_hp = 60
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 8  # Extrêmement rapide
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 150  # Change très souvent

        # Mouvement téléportation
        self.teleport_cooldown = 240
        self.last_teleport = -240
        self.is_teleporting = False
        self.teleport_timer = 0
        self.teleport_duration = 30
        self.teleport_target = (0, 0)

        # Animation de dégâts
        self.damage_animation_active = False
        self.damage_animation_duration = 10
        self.damage_animation_timer = 0
        self.damage_flash_interval = 2

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 360
        self.death_explosion_timer = 0
        self.death_explosions = []

        # Mode rage (activé quand HP < 30%)
        self.rage_mode = False
        self.rage_pulse = 0

        # Clone (illusion)
        self.clone_active = False
        self.clone_position = (0, 0)
        self.clone_timer = 0
        self.clone_duration = 180

        # Bouclier rotatif
        self.shield_orbs = []
        self.shield_active = False
        self.shield_orb_count = 6
        self.shield_rotation = 0

        # Pulsation visuelle
        self.pulse_timer = 0
        self.eye_glow = 0

    def _create_boss_sprite(self):
        """Crée un sprite procédural pour le Boss 5 - Entité cosmique/Œil du chaos"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Tentacules/rayons organiques
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

        # Corps principal - forme organique
        pygame.draw.circle(surf, (20, 60, 40), (center, center), 50)
        pygame.draw.circle(surf, (30, 100, 60), (center, center), 45)
        pygame.draw.circle(surf, (0, 150, 80), (center, center), 50, 3)

        # Motif hexagonal interne
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            hx = center + math.cos(angle) * 30
            hy = center + math.sin(angle) * 30
            hex_points.append((hx, hy))
        pygame.draw.polygon(surf, (0, 80, 50), hex_points)
        pygame.draw.polygon(surf, (0, 200, 100), hex_points, 2)

        # Œil central principal
        pygame.draw.circle(surf, (0, 0, 0), (center, center), 22)
        pygame.draw.circle(surf, (0, 255, 100), (center, center), 18)
        pygame.draw.circle(surf, (200, 255, 200), (center, center), 10)
        pygame.draw.circle(surf, (0, 100, 50), (center, center), 5)

        # Petits yeux secondaires
        for i in range(3):
            angle = math.radians(120 * i - 90)
            ex = center + math.cos(angle) * 35
            ey = center + math.sin(angle) * 35
            pygame.draw.circle(surf, (0, 0, 0), (int(ex), int(ey)), 8)
            pygame.draw.circle(surf, (0, 255, 100), (int(ex), int(ey)), 6)
            pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 3)

        return surf

    def _create_damaged_sprite(self):
        """Crée un sprite endommagé"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 180))
        surf.blit(flash, (0, 0))
        return surf

    def _create_rage_sprite(self):
        """Crée un sprite en mode rage"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Tentacules plus agressifs (rouges)
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

        # Corps en rage
        pygame.draw.circle(surf, (80, 20, 20), (center, center), 50)
        pygame.draw.circle(surf, (150, 30, 30), (center, center), 45)
        pygame.draw.circle(surf, (255, 50, 50), (center, center), 50, 3)

        # Hexagone
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30 + self.rage_pulse * 2)
            hx = center + math.cos(angle) * 30
            hy = center + math.sin(angle) * 30
            hex_points.append((hx, hy))
        pygame.draw.polygon(surf, (100, 0, 0), hex_points)
        pygame.draw.polygon(surf, (255, 100, 0), hex_points, 2)

        # Œil central en rage
        pygame.draw.circle(surf, (0, 0, 0), (center, center), 22)
        pygame.draw.circle(surf, (255, 50, 0), (center, center), 18)
        pygame.draw.circle(surf, (255, 200, 100), (center, center), 10)
        pygame.draw.circle(surf, (150, 0, 0), (center, center), 5)

        # Yeux secondaires
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

        # Vérifier mode rage
        if self.hp <= self.max_hp * 0.3 and not self.rage_mode:
            self.rage_mode = True
            self.shoot_delay_frames = 5  # Encore plus rapide en rage
            print("Boss 5: MODE RAGE ACTIVÉ!")

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

        # Téléportation
        if self.is_teleporting:
            self.teleport_timer += 1
            if self.teleport_timer >= self.teleport_duration // 2 and self.rect.center != self.teleport_target:
                self.rect.center = self.teleport_target
            if self.teleport_timer >= self.teleport_duration:
                self.is_teleporting = False
                self.teleport_timer = 0
            return False

        # Animation de dégâts
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

        # Gestion du clone
        if self.clone_active:
            self.clone_timer += 1
            if self.clone_timer >= self.clone_duration:
                self.clone_active = False
                self.clone_timer = 0

        # Déplacement vers la position
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 5 en position de combat!")
        else:
            # Mouvement erratique
            move_x = math.sin(self.timer * 0.03) * 3 + math.cos(self.timer * 0.02) * 2
            move_y = math.cos(self.timer * 0.025) * 2
            self.rect.x += int(move_x)
            self.rect.y = self.target_y + int(math.sin(self.timer * 0.015) * 40)

            # Garder dans les limites
            self.rect.x = max(100, min(SCREEN_WIDTH - 100, self.rect.x))

            # Téléportation périodique (plus fréquent en rage)
            tp_cooldown = self.teleport_cooldown // 2 if self.rage_mode else self.teleport_cooldown
            if self.timer - self.last_teleport >= tp_cooldown and player_position:
                self.is_teleporting = True
                self.teleport_timer = 0
                self.last_teleport = self.timer
                # Téléporter vers une position aléatoire
                self.teleport_target = (
                    random.randint(150, SCREEN_WIDTH - 150),
                    random.randint(80, 200)
                )
                print("Boss 5: Téléportation!")

            # Tir
            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    num_patterns = 8 if self.rage_mode else 6
                    pattern_index = (self.timer // self.pattern_switch_interval) % num_patterns
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns chaotiques du Boss 5"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 30

        if pattern_index == 0:
            # Pattern 0: Zigzag multiples
            for i in range(5):
                offset_x = (i - 2) * 50
                projectiles.append(ZigZagProjectile(bx + offset_x, by, 1, speed=5,
                                                   amplitude=40 + i * 10, frequency=0.08 + i * 0.02))
            print("Boss 5: Zigzag!")

        elif pattern_index == 1:
            # Pattern 1: Tirs paraboliques (gravité)
            for angle_deg in [-60, -30, 0, 30, 60]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad) * 0.3
                projectiles.append(GravityProjectile(bx, by, dx, dy, speed=6))
            print("Boss 5: Tirs paraboliques!")

        elif pattern_index == 2:
            # Pattern 2: Projectiles téléporteurs
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
            print("Boss 5: Tirs téléporteurs!")

        elif pattern_index == 3:
            # Pattern 3: Spirale double sens
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
            # Pattern 4: Mur ondulant
            for i in range(11):
                offset_x = (i - 5) * 40
                wave_offset = math.sin(i * 0.5 + self.timer * 0.1) * 0.3
                projectiles.append(Boss5Projectile(bx + offset_x, by, wave_offset, 1, speed=6))
            print("Boss 5: Mur ondulant!")

        elif pattern_index == 5:
            # Pattern 5: Activer le clone
            if not self.clone_active:
                self.clone_active = True
                self.clone_timer = 0
                # Position du clone de l'autre côté
                self.clone_position = (SCREEN_WIDTH - self.rect.centerx, self.rect.centery)
                print("Boss 5: Clone activé!")
            # Tir depuis le clone aussi
            cx, cy = self.clone_position
            px, py = player_position
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(Boss5Projectile(cx, cy + 60, dx, dy, speed=7))

        # Patterns rage uniquement
        elif pattern_index == 6 and self.rage_mode:
            # Pattern 6: Tempête de projectiles
            for i in range(16):
                angle = (2 * math.pi / 16) * i + self.timer * 0.1
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss5Projectile(bx, by, dx, dy, speed=5))
            print("Boss 5: TEMPÊTE!")

        elif pattern_index == 7 and self.rage_mode:
            # Pattern 7: Tout en même temps (chaos total)
            # Quelques zigzags
            projectiles.append(ZigZagProjectile(bx, by, 1, speed=6, amplitude=60, frequency=0.1))
            # Quelques gravités
            projectiles.append(GravityProjectile(bx - 50, by, -0.3, 0.2, speed=5))
            projectiles.append(GravityProjectile(bx + 50, by, 0.3, 0.2, speed=5))
            # Spirale
            for i in range(4):
                angle = math.radians(self.timer * 5 + i * 90)
                projectiles.append(Boss5Projectile(bx, by, math.cos(angle), math.sin(angle), speed=4))
            print("Boss 5: CHAOS TOTAL!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des dégâts au boss"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        # Effet de pulsation
        pulse = abs(math.sin(self.pulse_timer * 0.03)) * 0.4 + 0.6

        if not self.is_dying:
            # Aura verte (ou rouge en rage)
            if self.rage_mode:
                aura_color = (150, 0, 0, 40)
            else:
                aura_color = (0, 150, 50, 40)
            aura_size = int(100 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color, (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            # Particules flottantes
            for i in range(8):
                angle = math.radians(self.pulse_timer * 1.5 + i * 45)
                radius = 90 + math.sin(self.pulse_timer * 0.05 + i) * 20
                px = self.rect.centerx + math.cos(angle) * radius
                py = self.rect.centery + math.sin(angle) * radius * 0.6
                color = (255, 100, 0) if self.rage_mode else (0, 255, 100)
                pygame.draw.circle(surface, color, (int(px), int(py)), 5)
                pygame.draw.circle(surface, WHITE, (int(px), int(py)), 2)

        # Effet de téléportation
        if self.is_teleporting:
            alpha = int(255 * (1 - self.teleport_timer / self.teleport_duration))
            tp_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            tp_surf.blit(self.image, (0, 0))
            tp_surf.set_alpha(alpha)
            surface.blit(tp_surf, self.rect)
            # Effet au point d'arrivée
            if self.teleport_timer >= self.teleport_duration // 2:
                target_alpha = int(255 * (self.teleport_timer - self.teleport_duration // 2) / (self.teleport_duration // 2))
                arrival_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                arrival_surf.blit(self.image, (0, 0))
                arrival_surf.set_alpha(target_alpha)
                arrival_rect = arrival_surf.get_rect(center=self.teleport_target)
                surface.blit(arrival_surf, arrival_rect)
            return

        # Dessiner le clone
        if self.clone_active:
            clone_alpha = int(150 + 50 * math.sin(self.clone_timer * 0.1))
            clone_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            clone_surf.blit(self.image, (0, 0))
            clone_surf.set_alpha(clone_alpha)
            clone_rect = clone_surf.get_rect(center=self.clone_position)
            surface.blit(clone_surf, clone_rect)

        surface.blit(self.image, self.rect)

        # Barre de rage
        if self.rage_mode:
            rage_text_surf = pygame.Surface((100, 20), pygame.SRCALPHA)
            rage_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.1)))
            pygame.draw.rect(rage_text_surf, (255, 0, 0, rage_alpha), (0, 0, 100, 20))
            surface.blit(rage_text_surf, (self.rect.centerx - 50, self.rect.top - 30))

        for exp in self.death_explosions:
            exp.draw(surface)


class Boss6Projectile(EnemyProjectile):
    """Projectile du Boss 6 - noir avec aura violette"""
    def __init__(self, x, y, dx, dy, speed=5):
        super().__init__(x, y, dx, dy, speed)
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (50, 0, 80), (6, 6), 6)
        pygame.draw.circle(self.image, (20, 0, 40), (6, 6), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 6

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(180 * (i / len(self.trail))) if self.trail else 0
            size = max(2, int(4 * (i / max(1, len(self.trail)))))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (100, 0, 150, alpha), (size, size), size)
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))
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
        self.orbit_time = 60  # Frames avant de foncer
        self.timer = 0
        self.target_x = target_x
        self.target_y = target_y
        self.launched = False

        # Position initiale sur l'orbite
        start_x = x + math.cos(self.orbit_angle) * self.orbit_radius
        start_y = y + math.sin(self.orbit_angle) * self.orbit_radius
        super().__init__(start_x, start_y, 0, 1, speed)

        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 180), (8, 8), 8)
        pygame.draw.circle(self.image, (200, 100, 255), (8, 8), 4)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.max_trail_length = 8
        self.trail = []

    def update(self):
        self.timer += 1
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        if not self.launched:
            # Phase d'orbite
            self.orbit_angle += self.orbit_speed
            self.orbit_radius -= 0.3  # Se rapproche du centre
            new_x = self.center_x + math.cos(self.orbit_angle) * max(10, self.orbit_radius)
            new_y = self.center_y + math.sin(self.orbit_angle) * max(10, self.orbit_radius)
            self.rect.center = (int(new_x), int(new_y))

            if self.timer >= self.orbit_time:
                self.launched = True
                # Calculer direction vers cible
                dx = self.target_x - self.rect.centerx
                dy = self.target_y - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.dx = dx / dist
                    self.dy = dy / dist
                self.speed = 8
        else:
            # Phase de lancement
            self.rect.x += int(self.dx * self.speed)
            self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            progress = i / max(1, len(self.trail))
            alpha = int(200 * progress)
            size = max(2, int(6 * progress))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (150, 50, 255, alpha), (size, size), size)
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        # Effet de rotation visuelle
        pulse = abs(math.sin(self.timer * 0.2)) * 3
        pygame.draw.circle(surface, (150, 50, 255), self.rect.center, int(8 + pulse))
        pygame.draw.circle(surface, (200, 150, 255), self.rect.center, 4)


class BlackHoleProjectile(EnemyProjectile):
    """Projectile stationnaire qui attire les projectiles du joueur"""
    def __init__(self, x, y, lifetime=180):
        super().__init__(x, y, 0, 0, 0)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = lifetime
        self.timer = 0
        self.pull_radius = 150
        self.pull_strength = 2
        self.trail = []

    def update(self):
        self.timer += 1

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, surface):
        # Effet de trou noir avec anneaux
        progress = self.timer / self.lifetime
        base_alpha = int(255 * (1 - progress * 0.5))

        # Anneaux extérieurs
        for i in range(3):
            ring_size = 20 - i * 5 + int(5 * abs(math.sin(self.timer * 0.1 + i)))
            ring_alpha = max(0, base_alpha - i * 50)
            ring_surf = pygame.Surface((ring_size*2 + 10, ring_size*2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (100, 0, 150, ring_alpha),
                             (ring_size + 5, ring_size + 5), ring_size, 2)
            surface.blit(ring_surf, (self.rect.centerx - ring_size - 5,
                                     self.rect.centery - ring_size - 5))

        # Centre noir
        pygame.draw.circle(surface, (20, 0, 30), self.rect.center, 12)
        pygame.draw.circle(surface, (0, 0, 0), self.rect.center, 8)


class MirrorProjectile(EnemyProjectile):
    """Projectile qui se duplique quand il atteint certaines positions"""
    def __init__(self, x, y, dx, dy, speed=4, can_split=True):
        super().__init__(x, y, dx, dy, speed)
        self.can_split = can_split
        self.split_y = y + 200  # Se divise après avoir parcouru 200 pixels
        self.has_split = False
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (180, 0, 255), [(5, 0), (10, 10), (0, 10)])
        self.rect = self.image.get_rect(center=(x, y))
        self.max_trail_length = 5
        self.children = []

    def update(self):
        super().update()
        if self.can_split and not self.has_split and self.rect.centery >= self.split_y:
            self.has_split = True

    def should_split(self):
        return self.can_split and self.has_split and not self.children

    def split(self):
        """Crée deux copies allant dans des directions opposées"""
        self.children = [
            MirrorProjectile(self.rect.centerx, self.rect.centery,
                           self.dx - 0.5, self.dy, self.speed, can_split=False),
            MirrorProjectile(self.rect.centerx, self.rect.centery,
                           self.dx + 0.5, self.dy, self.speed, can_split=False)
        ]
        return self.children


class PulseWaveProjectile(EnemyProjectile):
    """Onde de choc circulaire qui s'étend"""
    def __init__(self, x, y, speed=3):
        super().__init__(x, y, 0, 0, speed)
        self.radius = 10
        self.max_radius = 300
        self.thickness = 8
        self.center = (x, y)
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.trail = []

    def update(self):
        self.radius += self.speed
        # Mettre à jour le rect pour les collisions (anneau)
        self.rect = pygame.Rect(
            self.center[0] - self.radius,
            self.center[1] - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def is_expired(self):
        return self.radius >= self.max_radius

    def check_collision(self, other_rect):
        """Collision spéciale pour l'anneau"""
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


class Boss6(Enemy):
    """Sixième Boss - Le Vortex du Néant avec des patterns gravitationnels"""
    def __init__(self, x, y, speed=2, target_y=80):
        self.size = 200
        self.hp = 70
        self.max_hp = 70
        self.speed = speed
        self.target_y = target_y
        self.timer = 0
        self.shoot_timer = 0
        self.shoot_delay_frames = 20
        self.shoot_count = 0  # Compteur de tirs pour patterns à fréquence variable
        self.pattern = 0
        self.pattern_timer = 0
        self.pattern_duration = 300
        self.is_dying = False
        self.death_timer = 0
        self.death_explosions = []

        # Mouvement de distorsion
        self.distortion_angle = 0
        self.distortion_amplitude = 30

        # Trou noir central (mécanique spéciale)
        self.black_hole_active = False
        self.black_hole_timer = 0
        self.black_hole_duration = 120
        self.black_hole_cooldown = 0

        # Phase de fureur (HP < 25%)
        self.fury_mode = False

        # Création du sprite (vortex/spirale)
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.create_sprite()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # Pour l'animation de rotation
        self.rotation_angle = 0

    def create_sprite(self):
        """Crée un sprite de vortex/spirale noir et violet"""
        center = self.size // 2

        # Fond avec dégradé circulaire
        for r in range(center, 0, -2):
            progress = r / center
            color_val = int(50 * progress)
            alpha = int(200 * progress)
            pygame.draw.circle(self.base_image, (color_val, 0, color_val + 30, alpha),
                             (center, center), r)

        # Spirales
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

        # Centre - œil du vortex
        pygame.draw.circle(self.base_image, (100, 0, 150), (center, center), 25)
        pygame.draw.circle(self.base_image, (50, 0, 80), (center, center), 18)
        pygame.draw.circle(self.base_image, (0, 0, 0), (center, center), 10)

    def take_damage(self, damage):
        if not self.black_hole_active:  # Invulnérable pendant le trou noir
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

        # Mouvement vers position cible avec distorsion
        if self.rect.centery < self.target_y:
            self.rect.y += self.speed
        else:
            # Mouvement de distorsion/ondulation
            offset_x = math.sin(self.distortion_angle) * self.distortion_amplitude
            offset_y = math.cos(self.distortion_angle * 0.7) * (self.distortion_amplitude * 0.5)
            base_x = SCREEN_WIDTH // 2 + offset_x

            self.rect.centerx = int(base_x)
            self.rect.centery = int(self.target_y + offset_y)

        # Gestion du trou noir
        if self.black_hole_cooldown > 0:
            self.black_hole_cooldown -= 1

        if self.black_hole_active:
            self.black_hole_timer += 1
            if self.black_hole_timer >= self.black_hole_duration:
                self.black_hole_active = False
                self.black_hole_timer = 0
                self.black_hole_cooldown = 300

        # Changement de pattern
        if self.pattern_timer >= self.pattern_duration:
            self.pattern_timer = 0
            if self.fury_mode:
                self.pattern = random.randint(0, 8)
            else:
                self.pattern = (self.pattern + 1) % 7

        # Tir
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay_frames and self.rect.centery >= self.target_y:
            self.shoot_timer = 0
            self.shoot(player_pos, projectiles_list)

        # Rotation du sprite
        self.image = pygame.transform.rotate(self.base_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        return False

    def shoot(self, player_pos, projectiles_list):
        cx, cy = self.rect.center
        self.shoot_count += 1

        if self.pattern == 0:
            # Pattern 0: Vortex - projectiles qui orbitent puis foncent
            # Tire 2 projectiles en positions opposées
            for i in range(2):
                angle = (i / 2) * 2 * math.pi + self.timer * 0.08
                spawn_x = cx + math.cos(angle) * 60
                spawn_y = cy + math.sin(angle) * 60
                proj = VortexProjectile(spawn_x, spawn_y, player_pos[0], player_pos[1])
                projectiles_list.append(proj)

        elif self.pattern == 1:
            # Pattern 1: Ondes de choc concentriques (une onde tous les 3 tirs)
            if self.shoot_count % 3 == 1:
                proj = PulseWaveProjectile(cx, cy, speed=4)
                projectiles_list.append(proj)

        elif self.pattern == 2:
            # Pattern 2: Pluie de miroirs qui se divisent (tous les 2 tirs)
            if self.shoot_count % 2 == 1:
                for i in range(3):
                    x = cx - 80 + i * 80
                    proj = MirrorProjectile(x, cy + 40, 0, 1, speed=4)
                    projectiles_list.append(proj)

        elif self.pattern == 3:
            # Pattern 3: Spirale inversée (tire vers l'intérieur puis explose)
            angle = self.timer * 0.15
            for offset in [0, math.pi]:
                spawn_x = cx + math.cos(angle + offset) * 100
                spawn_y = cy + math.sin(angle + offset) * 100
                dx = -math.cos(angle + offset)
                dy = -math.sin(angle + offset) + 0.5
                proj = Boss6Projectile(spawn_x, spawn_y, dx, dy, speed=3)
                projectiles_list.append(proj)

        elif self.pattern == 4:
            # Pattern 4: Trou noir - crée un trou noir qui attire
            if not self.black_hole_active and self.black_hole_cooldown == 0:
                self.black_hole_active = True
                self.black_hole_timer = 0
                proj = BlackHoleProjectile(cx, cy + 150, lifetime=self.black_hole_duration)
                projectiles_list.append(proj)
            # Tire aussi des projectiles normaux pendant le trou noir
            for i in range(6):
                angle = (i / 6) * 2 * math.pi
                dx = math.cos(angle)
                dy = math.sin(angle)
                proj = Boss6Projectile(cx, cy, dx, dy, speed=4)
                projectiles_list.append(proj)

        elif self.pattern == 5:
            # Pattern 5: Mur de distorsion ondulant (tous les 2 tirs)
            if self.shoot_count % 2 == 0:
                for i in range(12):
                    x = (i / 11) * SCREEN_WIDTH
                    wave_offset = math.sin(i * 0.5 + self.timer * 0.1) * 30
                    proj = Boss6Projectile(x, cy + 50 + wave_offset, 0, 1, speed=3)
                    projectiles_list.append(proj)

        elif self.pattern == 6:
            # Pattern 6: Étoiles filantes - trajectoires courbes
            side = 1 if self.shoot_count % 2 == 0 else -1
            start_x = cx + side * 80
            dx = -side * 0.3
            dy = 1
            proj = Boss6Projectile(start_x, cy + 30, dx, dy, speed=5)
            projectiles_list.append(proj)

        # Patterns de fureur
        if self.fury_mode:
            if self.pattern == 7:
                # Pattern 7: Double vortex
                for side in [-1, 1]:
                    for i in range(3):
                        angle = (i / 3) * 2 * math.pi + self.timer * 0.1
                        spawn_x = cx + side * 60 + math.cos(angle) * 40
                        spawn_y = cy + math.sin(angle) * 40
                        proj = VortexProjectile(spawn_x, spawn_y,
                                               player_pos[0], player_pos[1])
                        projectiles_list.append(proj)

            elif self.pattern == 8:
                # Pattern 8: Apocalypse - tout en même temps
                if self.shoot_count % 2 == 0:
                    # Onde de choc
                    projectiles_list.append(PulseWaveProjectile(cx, cy, speed=5))
                # Spirale
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

        # Effet de rétrécissement et rotation accélérée
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
        # Effet d'aura pendant le mode trou noir
        if self.black_hole_active:
            pulse = abs(math.sin(self.timer * 0.15)) * 20
            aura_surf = pygame.Surface((self.size + 60, self.size + 60), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (100, 0, 150, 100),
                             (self.size//2 + 30, self.size//2 + 30),
                             int(self.size//2 + 20 + pulse))
            surface.blit(aura_surf, (self.rect.centerx - self.size//2 - 30,
                                     self.rect.centery - self.size//2 - 30))

        surface.blit(self.image, self.rect)

        # Indicateur de fureur
        if self.fury_mode:
            fury_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.15)))
            fury_surf = pygame.Surface((120, 25), pygame.SRCALPHA)
            pygame.draw.rect(fury_surf, (100, 0, 150, fury_alpha), (0, 0, 120, 25))
            surface.blit(fury_surf, (self.rect.centerx - 60, self.rect.top - 35))

        for exp in self.death_explosions:
            exp.draw(surface)


class Level:
    def __init__(self):
        self.background = Background(speed=2)
        self.timer = 0
        self.enemies = []
        self.spawn_events = [
            (180, lambda: self.spawn_enemies(3)),
            (300, lambda: self.spawn_formation_v(5)),
            (480, lambda: self.spawn_sine_wave_group(4)),
            (600, lambda: self.spawn_zigzag_group(3)),
            (720, lambda: self.spawn_formation_line(6)),
            (840, lambda: self.spawn_swoop_attack()),
            (900, lambda: self.spawn_shooting_enemy(1)),
            (1020, lambda: self.spawn_horizontal_squadron()),
            (1200, lambda: self.spawn_boss())
        ]
        self.spawn_events.sort(key=lambda event: event[0])

        # Système de spawn du Boss 2
        self.boss1_defeated = False
        self.boss1_defeat_timer = 0
        self.boss2_spawn_delay = 600  # 10 secondes à 60 FPS
        self.boss2_spawned = False

        # Système de spawn du Boss 3
        self.boss2_defeated = False
        self.boss2_defeat_timer = 0
        self.boss3_spawn_delay = 600  # 10 secondes à 60 FPS
        self.boss3_spawned = False

        # Système de spawn du Boss 4
        self.boss3_defeated = False
        self.boss3_defeat_timer = 0
        self.boss4_spawn_delay = 600  # 10 secondes à 60 FPS
        self.boss4_spawned = False

        # Système de spawn du Boss 5
        self.boss4_defeated = False
        self.boss4_defeat_timer = 0
        self.boss5_spawn_delay = 600  # 10 secondes à 60 FPS
        self.boss5_spawned = False

        # Système de spawn du Boss 6
        self.boss5_defeated = False
        self.boss5_defeat_timer = 0
        self.boss6_spawn_delay = 600  # 10 secondes à 60 FPS
        self.boss6_spawned = False

    def spawn_enemies(self, count):
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            enemy = Enemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} enemies at timer {self.timer}')

    def spawn_shooting_enemy(self, count):
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            enemy = ShootingEnemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} shooting enemy at timer {self.timer}')

    def spawn_boss(self):
        boss = Boss(SCREEN_WIDTH // 2, -50)
        self.enemies.append(boss)
        print(f'Spawned boss at timer {self.timer}')

    def spawn_boss2(self):
        boss2 = Boss2(SCREEN_WIDTH // 2, -70)
        self.enemies.append(boss2)
        self.boss2_spawned = True
        print(f'Spawned Boss 2 at timer {self.timer}')

    def spawn_boss3(self):
        boss3 = Boss3(SCREEN_WIDTH // 2, -80)
        self.enemies.append(boss3)
        self.boss3_spawned = True
        print(f'Spawned Boss 3 at timer {self.timer}')

    def spawn_boss4(self):
        boss4 = Boss4(SCREEN_WIDTH // 2, -90)
        self.enemies.append(boss4)
        self.boss4_spawned = True
        print(f'Spawned Boss 4 at timer {self.timer}')

    def spawn_boss5(self):
        boss5 = Boss5(SCREEN_WIDTH // 2, -100)
        self.enemies.append(boss5)
        self.boss5_spawned = True
        print(f'Spawned Boss 5 at timer {self.timer}')

    def spawn_boss6(self):
        boss6 = Boss6(SCREEN_WIDTH // 2, -110)
        self.enemies.append(boss6)
        self.boss6_spawned = True
        print(f'Spawned Boss 6 at timer {self.timer}')

    def spawn_formation_v(self, count):
        """Spawn des ennemis en formation V"""
        center_x = SCREEN_WIDTH // 2
        spacing = 60
        for i in range(count):
            offset = (i - count // 2) * spacing
            y_offset = abs(i - count // 2) * 30
            enemy = Enemy(center_x + offset, -20 - y_offset, speed=2.5)
            enemy.image.fill(CYAN)
            self.enemies.append(enemy)
        print(f'Spawned V formation with {count} enemies at timer {self.timer}')

    def spawn_formation_line(self, count):
        """Spawn des ennemis en ligne horizontale"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            enemy = Enemy(x, -20, speed=2)
            enemy.image.fill(ORANGE)
            self.enemies.append(enemy)
        print(f'Spawned line formation with {count} enemies at timer {self.timer}')

    def spawn_sine_wave_group(self, count):
        """Spawn des ennemis avec mouvement sinusoïdal"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            pattern = SineWavePattern(amplitude=80, frequency=0.05, base_speed=2.5)
            enemy = Enemy(x, -20, movement_pattern=pattern)
            enemy.image.fill((255, 100, 200))
            self.enemies.append(enemy)
        print(f'Spawned {count} sine wave enemies at timer {self.timer}')

    def spawn_zigzag_group(self, count):
        """Spawn des ennemis avec mouvement zigzag"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            pattern = ZigZagPattern(amplitude=60, switch_time=25, base_speed=3)
            enemy = Enemy(x, -20, movement_pattern=pattern)
            enemy.image.fill((100, 255, 100))
            self.enemies.append(enemy)
        print(f'Spawned {count} zigzag enemies at timer {self.timer}')

    def spawn_swoop_attack(self):
        """Spawn des ennemis qui font un piqué depuis les côtés"""
        # Ennemi gauche qui pique à droite
        pattern_right = SwoopPattern(swoop_direction=1)
        enemy_left = Enemy(50, -20, movement_pattern=pattern_right)
        enemy_left.image.fill((255, 200, 0))
        self.enemies.append(enemy_left)

        # Ennemi droit qui pique à gauche
        pattern_left = SwoopPattern(swoop_direction=-1)
        enemy_right = Enemy(SCREEN_WIDTH - 50, -20, movement_pattern=pattern_left)
        enemy_right.image.fill((255, 200, 0))
        self.enemies.append(enemy_right)

        # l'un des deux drop
        powerup_dropper = random.choice([enemy_left, enemy_right])
        powerup_dropper.drops_powerup = True

        print(f'Spawned swoop attack at timer {self.timer}')

    def spawn_horizontal_squadron(self):
        """Spawn une escadrille qui se déplace horizontalement"""
        y_positions = [-20, -80, -140]
        for i, y in enumerate(y_positions):
            direction = 1 if i % 2 == 0 else -1
            start_x = 50 if direction == 1 else SCREEN_WIDTH - 50
            pattern = HorizontalWavePattern(direction=direction, speed=5)
            enemy = Enemy(start_x, y, movement_pattern=pattern)
            enemy.image.fill((150, 150, 255))
            self.enemies.append(enemy)
        print(f'Spawned horizontal squadron at timer {self.timer}')

    def update(self):
        self.background.update()
        self.timer += 1
        events_to_remove = []
        for event in self.spawn_events:
            if self.timer >= event[0]:
                event[1]()
                events_to_remove.append(event)
        for event in events_to_remove:
            self.spawn_events.remove(event)
        for enemy in self.enemies:
            if not isinstance(enemy, (ShootingEnemy, Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                enemy.update()
        self.enemies = [e for e in self.enemies if (e.rect.top < SCREEN_HEIGHT or isinstance(e, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)))]

        # Gestion du spawn du Boss 2 après défaite du Boss 1
        if self.boss1_defeated and not self.boss2_spawned:
            self.boss1_defeat_timer += 1
            if self.boss1_defeat_timer >= self.boss2_spawn_delay:
                self.spawn_boss2()

        # Gestion du spawn du Boss 3 après défaite du Boss 2
        if self.boss2_defeated and not self.boss3_spawned:
            self.boss2_defeat_timer += 1
            if self.boss2_defeat_timer >= self.boss3_spawn_delay:
                self.spawn_boss3()

        # Gestion du spawn du Boss 4 après défaite du Boss 3
        if self.boss3_defeated and not self.boss4_spawned:
            self.boss3_defeat_timer += 1
            if self.boss3_defeat_timer >= self.boss4_spawn_delay:
                self.spawn_boss4()

        # Gestion du spawn du Boss 5 après défaite du Boss 4
        if self.boss4_defeated and not self.boss5_spawned:
            self.boss4_defeat_timer += 1
            if self.boss4_defeat_timer >= self.boss5_spawn_delay:
                self.spawn_boss5()

        # Gestion du spawn du Boss 6 après défaite du Boss 5
        if self.boss5_defeated and not self.boss6_spawned:
            self.boss5_defeat_timer += 1
            if self.boss5_defeat_timer >= self.boss6_spawn_delay:
                self.spawn_boss6()

        if any(isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) for enemy in self.enemies):
            if self.background.speed > 0:
                self.background.speed = max(self.background.speed - 0.05, 0)
        else:
            if self.background.speed < self.background.default_speed:
                self.background.speed = min(self.background.speed + 0.05, self.background.default_speed)

    def draw(self, surface):
        self.background.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

class Projectile:
    def __init__(self, x, y, speed=10):
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.trail = []
        self.max_trail_length = 6

        self.trail_cache = []
        for i in range(self.max_trail_length):
            progress = i / self.max_trail_length if self.max_trail_length > 0 else 0
            alpha = int(255 * progress)
            size = max(1, int(4 * progress))
            color = (int(200 + 55 * progress), 255, 0, alpha)
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            self.trail_cache.append((trail_surf, size))

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.y -= self.speed

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            trail_surf, size = self.trail_cache[i]
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        surface.blit(self.image, self.rect)


class SpreadProjectile(Projectile):
    """Projectile qui se déplace en diagonale pour le tir en éventail"""
    def __init__(self, x, y, speed=10, angle=15):
        super().__init__(x, y, speed)
        self.angle = angle
        angle_rad = math.radians(angle)
        self.dx = math.sin(angle_rad) * speed
        self.dy = -math.cos(angle_rad) * speed

    def update(self):
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("sprites/Spaceship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
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

        # Effet de réacteur (thruster)
        self.thruster_particles = []
        self.thruster_timer = 0

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos
        if self.invulnerable:
            now = pygame.time.get_ticks()
            if now - self.invuln_start >= self.invuln_duration:
                self.invulnerable = False

        if self.power_type != 'normal':
            now = pygame.time.get_ticks()
            if now - self.power_start >= self.power_duration:
                self.power_type = 'normal'
                print("Power-up expiré!")

        # Mise à jour de l'effet de réacteur
        self.thruster_timer += 1
        if self.thruster_timer % 2 == 0:
            # Créer de nouvelles particules de feu
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

        # Mise à jour des particules existantes
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
        print(f"Power-up '{power_type}' activé!")

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
                projectile_list.append(Projectile(cx, cy))  # Centre
                projectile_list.append(SpreadProjectile(cx, cy, angle=15))

            self.last_shot = now

    def draw(self, surface):
        # Dessiner l'effet de réacteur (avant le vaisseau)
        for p in self.thruster_particles:
            progress = p['life'] / p['max_life']
            size = int(p['size'])
            if size < 1:
                continue

            # Couleur qui passe de jaune/blanc (centre) à orange puis rouge
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

            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            if self.power_type == 'double':
                color = CYAN
            elif self.power_type == 'triple':
                color = (255, 0, 255)
            elif self.power_type == 'spread':
                color = (0, 255, 100)
            else:
                color = WHITE
            pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_width * progress), bar_height))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Wave")
    clock = pygame.time.Clock()
    running = True

    level = Level()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemy_projectiles = []
    explosions = []
    powerups = []
    combo = ComboSystem()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        level.update()
        player.update()
        for projectile in projectiles:
            projectile.update()
        # Détecter les tirs qui quittent l'écran sans toucher - reset le combo
        projectiles_avant = len(projectiles)
        projectiles = [p for p in projectiles if p.rect.bottom > 0]
        tirs_rates = projectiles_avant - len(projectiles)
        if tirs_rates > 0:
            combo.miss()

        for enemy in level.enemies[:]:
            if isinstance(enemy, Boss):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(5):
                        rand_x = enemy.rect.left + random.randint(0, 100)
                        rand_y = enemy.rect.top + random.randint(0, 100)
                        explosions.append(Explosion(rand_x, rand_y, duration=500))
                    print("Boss 1 vaincu !")
                    level.boss1_defeated = True
            elif isinstance(enemy, Boss2):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(8):
                        rand_x = enemy.rect.left + random.randint(0, 120)
                        rand_y = enemy.rect.top + random.randint(0, 120)
                        explosions.append(Explosion(rand_x, rand_y, duration=600))
                    print("Boss 2 vaincu !")
                    level.boss2_defeated = True
            elif isinstance(enemy, Boss3):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(12):
                        rand_x = enemy.rect.left + random.randint(0, 140)
                        rand_y = enemy.rect.top + random.randint(0, 140)
                        explosions.append(Explosion(rand_x, rand_y, duration=700))
                    print("Boss 3 vaincu !")
                    level.boss3_defeated = True
            elif isinstance(enemy, Boss4):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(20):
                        rand_x = enemy.rect.left + random.randint(0, 160)
                        rand_y = enemy.rect.top + random.randint(0, 160)
                        explosions.append(Explosion(rand_x, rand_y, duration=800))
                    print("Boss 4 vaincu !")
                    level.boss4_defeated = True
            elif isinstance(enemy, Boss5):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(30):
                        rand_x = enemy.rect.left + random.randint(0, 180)
                        rand_y = enemy.rect.top + random.randint(0, 180)
                        explosions.append(Explosion(rand_x, rand_y, duration=1000))
                    print("Boss 5 vaincu !")
                    level.boss5_defeated = True
            elif isinstance(enemy, Boss6):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(40):
                        rand_x = enemy.rect.left + random.randint(0, 200)
                        rand_y = enemy.rect.top + random.randint(0, 200)
                        explosions.append(Explosion(rand_x, rand_y, duration=1200))
                    print("Boss 6 vaincu ! VICTOIRE ULTIME !")
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(player.rect.center, enemy_projectiles)

        for e_proj in enemy_projectiles:
            if isinstance(e_proj, HomingProjectile):
                e_proj.update(player.rect.center)
            else:
                e_proj.update()

        # Gérer les projectiles qui se divisent (SplittingProjectile et MirrorProjectile)
        new_split_projectiles = []
        for e_proj in enemy_projectiles:
            if isinstance(e_proj, SplittingProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
            elif isinstance(e_proj, MirrorProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
        enemy_projectiles.extend(new_split_projectiles)

        # Filtrer les projectiles hors écran et les projectiles expirés
        enemy_projectiles = [p for p in enemy_projectiles if (
            p.rect.top < SCREEN_HEIGHT and
            p.rect.left < SCREEN_WIDTH and
            p.rect.right > 0 and
            p.rect.bottom > 0 and
            not (isinstance(p, HomingProjectile) and p.is_expired()) and
            not (isinstance(p, BlackHoleProjectile) and p.is_expired()) and
            not (isinstance(p, PulseWaveProjectile) and p.is_expired())
        )]

        for projectile in projectiles[:]:
            for enemy in level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                        continue
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    combo.hit()  # Prolonge le combo
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(1)
                        if isinstance(enemy, Boss):
                            boss_name = "Boss 1"
                        elif isinstance(enemy, Boss2):
                            boss_name = "Boss 2"
                        elif isinstance(enemy, Boss3):
                            boss_name = "Boss 3"
                        elif isinstance(enemy, Boss4):
                            boss_name = "Boss 4"
                        elif isinstance(enemy, Boss5):
                            boss_name = "Boss 5"
                        else:
                            boss_name = "Boss 6"
                        print(f'{boss_name} touché ! HP restant : {enemy.hp}')
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            print(f"{boss_name} en train de mourir...")
                    else:
                        if enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            powerups.append(powerup)
                            print(f"Power-up '{chosen_power}' largué !")
                        level.enemies.remove(enemy)
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    break

        for e_proj in enemy_projectiles[:]:
            # Collision spéciale pour PulseWaveProjectile (onde de choc)
            if isinstance(e_proj, PulseWaveProjectile):
                if e_proj.check_collision(player.rect):
                    if not player.invulnerable:
                        player.hp -= 1
                        print(f'Player touché par onde de choc ! HP restant : {player.hp}')
                        if player.hp <= 0:
                            print("Player éliminé ! Game Over.")
                            running = False
                        else:
                            player.invulnerable = True
                            player.invuln_start = pygame.time.get_ticks()
            elif e_proj.rect.colliderect(player.rect):
                try:
                    enemy_projectiles.remove(e_proj)
                except ValueError:
                    pass
                if not player.invulnerable:
                    player.hp -= 1
                    print(f'Player touché par projectile ! HP restant : {player.hp}')
                    if player.hp <= 0:
                        print("Player éliminé ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for enemy in level.enemies[:]:
            if enemy.rect.colliderect(player.rect):
                if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                    continue
                # Collision avec Boss4 en charge = dégâts massifs
                if isinstance(enemy, Boss4) and enemy.charging:
                    if not player.invulnerable:
                        player.hp -= 3
                        print(f'Player écrasé par la charge ! HP restant : {player.hp}')
                        if player.hp <= 0:
                            print("Player éliminé ! Game Over.")
                            running = False
                        else:
                            player.invulnerable = True
                            player.invuln_start = pygame.time.get_ticks()
                    continue
                if not player.invulnerable:
                    player.hp -= player.contact_damage
                    print(f'Player touché par ennemi ! HP restant : {player.hp}')
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(player.contact_damage)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            if isinstance(enemy, Boss):
                                boss_name = "Boss 1"
                            elif isinstance(enemy, Boss2):
                                boss_name = "Boss 2"
                            elif isinstance(enemy, Boss3):
                                boss_name = "Boss 3"
                            elif isinstance(enemy, Boss4):
                                boss_name = "Boss 4"
                            elif isinstance(enemy, Boss5):
                                boss_name = "Boss 5"
                            else:
                                boss_name = "Boss 6"
                            print(f"{boss_name} en train de mourir...")
                    else:
                        enemy.hp -= player.contact_damage
                    impact_x = (player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (player.rect.centery + enemy.rect.centery) // 2
                    explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0 and not isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        if hasattr(enemy, 'drops_powerup') and enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            powerups.append(powerup)
                            print(f"Power-up '{chosen_power}' largué !")
                        level.enemies.remove(enemy)
                    if player.hp <= 0:
                        print("Player éliminé ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        # Collision avec le laser du Boss 3
        for enemy in level.enemies:
            if isinstance(enemy, Boss3) and enemy.laser_active and not player.invulnerable:
                laser_rect = pygame.Rect(enemy.laser_target_x - 25, 0, 50, SCREEN_HEIGHT)
                if player.rect.colliderect(laser_rect):
                    player.hp -= 2
                    print(f'Player touché par laser ! HP restant : {player.hp}')
                    if player.hp <= 0:
                        print("Player éliminé ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if not exp.is_finished()]

        for powerup in powerups:
            powerup.update()
        powerups = [p for p in powerups if p.rect.top < SCREEN_HEIGHT]

        for powerup in powerups[:]:
            if powerup.rect.colliderect(player.rect):
                player.apply_powerup(powerup.power_type)
                try:
                    powerups.remove(powerup)
                except ValueError:
                    pass

        combo.update()

        screen.fill(BLACK)
        level.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        for e_proj in enemy_projectiles:
            e_proj.draw(screen)
        for powerup in powerups:
            powerup.draw(screen)
        player.draw(screen)
        for exp in explosions:
            exp.draw(screen)

        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Timer: {level.timer}", True, WHITE)
        screen.blit(timer_text, (10, 10))
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 50))

        combo.draw(screen, font)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
