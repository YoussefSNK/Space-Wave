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
            if not isinstance(enemy, (ShootingEnemy, Boss)):
                enemy.update()
        self.enemies = [e for e in self.enemies if (e.rect.top < SCREEN_HEIGHT or isinstance(e, Boss))]

        if any(isinstance(enemy, Boss) for enemy in self.enemies):
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
                    print("Boss vaincu !")
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(player.rect.center, enemy_projectiles)

        for e_proj in enemy_projectiles:
            e_proj.update()
        enemy_projectiles = [p for p in enemy_projectiles if (p.rect.top < SCREEN_HEIGHT and 
                                                              p.rect.left < SCREEN_WIDTH and 
                                                              p.rect.right > 0)]

        for projectile in projectiles[:]:
            for enemy in level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, Boss) and enemy.is_dying:
                        continue
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    combo.hit()  # Prolonge le combo
                    if isinstance(enemy, Boss):
                        enemy.take_damage(1)
                        print(f'Boss touché ! HP restant : {enemy.hp}')
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            print("Boss en train de mourir...")
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
            if e_proj.rect.colliderect(player.rect):
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
                if isinstance(enemy, Boss) and enemy.is_dying:
                    continue
                if not player.invulnerable:
                    player.hp -= player.contact_damage
                    print(f'Player touché par ennemi ! HP restant : {player.hp}')
                    if isinstance(enemy, Boss):
                        enemy.take_damage(player.contact_damage)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            print("Boss en train de mourir...")
                    else:
                        enemy.hp -= player.contact_damage
                    impact_x = (player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (player.rect.centery + enemy.rect.centery) // 2
                    explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0 and not isinstance(enemy, Boss):
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
