import pygame
import random
import math

from config import SCREEN_WIDTH, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import (
    Boss9Projectile, VoidFeatherProjectile, SoulFireProjectile,
    AnnihilationOrbProjectile, PhoenixWaveProjectile
)


class Boss9(Enemy):
    """Neuvieme Boss - Le Void Phoenix, entite cosmique de feu noir et de neant"""
    def __init__(self, x, y, speed=2, target_y=100):
        super().__init__(x, y, speed)

        self.size = 220
        self.hp = 100
        self.max_hp = 100
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 14
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 200

        # Animation des ailes
        self.wing_angle = 0
        self.wing_flap_speed = 0.08
        self.wing_spread = 1.0  # 0.0 = repliees, 1.0 = deployees

        # Rotation et pulsation du corps
        self.body_rotation = 0
        self.core_pulse = 0
        self.flame_timer = 0

        # Particules de flammes du void
        self.void_particles = []
        self.max_particles = 30

        # Phase 2: Renaissance (Rebirth)
        self.rebirth_mode = False
        self.rebirth_pulse = 0
        self.rebirth_transition = False
        self.rebirth_transition_timer = 0
        self.rebirth_transition_duration = 120
        self.rebirth_flash_alpha = 0

        # Flammes spectrales autour du boss
        self.spectral_flames = []
        self.num_flames = 12
        for i in range(self.num_flames):
            self.spectral_flames.append({
                'angle': (2 * math.pi / self.num_flames) * i,
                'radius': 90 + random.randint(-10, 10),
                'height': random.randint(20, 40),
                'speed': random.uniform(0.02, 0.04),
                'phase': random.uniform(0, 2 * math.pi)
            })

        # Plumes qui tombent periodiquement
        self.falling_feathers = []
        self.feather_spawn_timer = 0
        self.feather_spawn_interval = 60

        # Animation de degats
        self.damage_animation_active = False
        self.damage_animation_duration = 15
        self.damage_animation_timer = 0
        self.damage_flash_interval = 3

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 450
        self.death_explosion_timer = 0
        self.death_explosions = []

        # Cri du phoenix (effet visuel d'onde)
        self.screech_active = False
        self.screech_timer = 0
        self.screech_waves = []

        self.pulse_timer = 0
        self.glow_intensity = 0

        # Creer le sprite initial
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_boss_sprite(self):
        """Cree un sprite procedural pour le Boss 9 - Void Phoenix"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Calculer l'amplitude des ailes
        wing_amplitude = math.sin(self.wing_angle) * 15 * self.wing_spread

        # Corps principal - forme ovale sombre avec aura violette
        body_points = []
        for i in range(20):
            angle = (2 * math.pi / 20) * i
            # Corps elliptique
            rx = 35 + math.sin(angle * 2 + self.core_pulse * 0.1) * 5
            ry = 45 + math.cos(angle * 3 + self.core_pulse * 0.1) * 5
            bx = center + math.cos(angle) * rx
            by = center + math.sin(angle) * ry
            body_points.append((bx, by))

        # Corps sombre avec degradé
        pygame.draw.polygon(surf, (30, 10, 50), body_points)
        # Contour violet
        pygame.draw.polygon(surf, (120, 40, 180), body_points, 3)

        # Ailes gauche et droite - formes elegantes de plumes
        self._draw_wing(surf, center, -1, wing_amplitude)  # Aile gauche
        self._draw_wing(surf, center, 1, wing_amplitude)   # Aile droite

        # Queue de flammes void
        self._draw_tail(surf, center)

        # Tete du phoenix
        head_y = center - 35
        # Crete de flammes sur la tete
        for i in range(5):
            flame_height = 15 + math.sin(self.flame_timer * 0.2 + i * 0.5) * 8
            flame_x = center + (i - 2) * 8
            color = self._get_void_flame_color(i * 0.3)
            points = [
                (flame_x, head_y),
                (flame_x - 4, head_y + flame_height),
                (flame_x + 4, head_y + flame_height)
            ]
            pygame.draw.polygon(surf, color, points)

        # Yeux perçants
        eye_glow = abs(math.sin(self.pulse_timer * 0.1)) * 50
        left_eye = (center - 12, center - 20)
        right_eye = (center + 12, center - 20)

        # Halo des yeux
        for eye_pos in [left_eye, right_eye]:
            pygame.draw.circle(surf, (150 + int(eye_glow), 50, 200), eye_pos, 8)
            pygame.draw.circle(surf, (200, 100, 255), eye_pos, 5)
            pygame.draw.circle(surf, WHITE, eye_pos, 2)

        # Noyau central brillant
        core_size = 18 + abs(math.sin(self.core_pulse * 0.05)) * 5
        pygame.draw.circle(surf, (60, 20, 100), (center, center), int(core_size))
        pygame.draw.circle(surf, (140, 60, 200), (center, center), int(core_size * 0.7))
        pygame.draw.circle(surf, (200, 150, 255), (center, center), int(core_size * 0.4))
        pygame.draw.circle(surf, WHITE, (center, center), int(core_size * 0.2))

        return surf

    def _draw_wing(self, surf, center, side, amplitude):
        """Dessine une aile du phoenix"""
        # side: -1 pour gauche, 1 pour droite
        wing_base_x = center + side * 30
        wing_base_y = center

        # Plusieurs couches de plumes
        for layer in range(4):
            layer_offset = layer * 12
            wing_length = 70 - layer * 10
            wing_angle_offset = math.radians(30 + layer * 15) * side

            # Points de l'aile avec courbe de Bezier simplifiee
            tip_x = wing_base_x + side * wing_length + side * amplitude
            tip_y = wing_base_y - 20 + layer_offset + amplitude * 0.5

            # Couleur degradee pour chaque couche
            if self.rebirth_mode:
                # Mode renaissance: couleurs incandescentes
                r = min(255, 200 + layer * 20)
                g = max(0, 100 - layer * 20)
                b = max(0, 50 - layer * 10)
                color = (r, g, b)
                edge_color = (255, min(255, 150 + layer * 30), 100)
            else:
                # Mode normal: violet/noir
                intensity = 80 + layer * 30
                color = (intensity // 2, 20, intensity)
                edge_color = (min(255, intensity + 50), 50, min(255, intensity + 80))

            # Dessiner les plumes principales
            for feather in range(5 - layer):
                feather_angle = (feather / (5 - layer)) * math.pi * 0.4 - math.pi * 0.2
                feather_length = (wing_length - layer * 8) * (1 - feather * 0.15)

                fx = wing_base_x + math.cos(wing_angle_offset + feather_angle) * feather_length * side
                fy = wing_base_y + math.sin(wing_angle_offset + feather_angle) * feather_length * 0.5 + layer_offset

                # Plume individuelle
                feather_points = [
                    (wing_base_x + side * layer * 5, wing_base_y + layer_offset),
                    (fx, fy),
                    (fx - side * 5, fy + 10)
                ]
                pygame.draw.polygon(surf, color, feather_points)
                pygame.draw.polygon(surf, edge_color, feather_points, 1)

    def _draw_tail(self, surf, center):
        """Dessine la queue de flammes du phoenix"""
        tail_base_y = center + 40

        for i in range(7):
            # Position de chaque flamme de queue
            offset_x = (i - 3) * 12
            flame_length = 35 + abs(i - 3) * (-8) + math.sin(self.flame_timer * 0.15 + i * 0.4) * 10

            # Couleurs des flammes
            if self.rebirth_mode:
                colors = [
                    (255, 200, 100),
                    (255, 150, 50),
                    (255, 100, 0),
                    (200, 50, 0)
                ]
            else:
                colors = [
                    (180, 100, 255),
                    (120, 50, 200),
                    (80, 20, 150),
                    (40, 10, 80)
                ]

            for c_idx, color in enumerate(colors):
                shrink = c_idx * 3
                points = [
                    (center + offset_x, tail_base_y),
                    (center + offset_x - 8 + shrink, tail_base_y + flame_length - shrink * 5),
                    (center + offset_x + 8 - shrink, tail_base_y + flame_length - shrink * 5)
                ]
                pygame.draw.polygon(surf, color, points)

    def _get_void_flame_color(self, offset=0):
        """Retourne une couleur de flamme void animee"""
        if self.rebirth_mode:
            # Flammes incandescentes oranges/jaunes
            phase = self.flame_timer * 0.1 + offset
            r = 255
            g = int(150 + 100 * math.sin(phase))
            b = int(50 + 50 * math.sin(phase * 2))
            return (r, g, b)
        else:
            # Flammes void violettes/noires
            phase = self.flame_timer * 0.1 + offset
            r = int(100 + 80 * math.sin(phase))
            g = int(30 + 30 * math.sin(phase * 1.5))
            b = int(150 + 100 * math.sin(phase))
            return (r, g, b)

    def _create_damaged_sprite(self):
        """Cree un sprite endommage avec flash blanc"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 220))
        surf.blit(flash, (0, 0))
        return surf

    def _create_rebirth_sprite(self):
        """Cree un sprite en mode renaissance - couleurs incandescentes"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        wing_amplitude = math.sin(self.wing_angle) * 20 * self.wing_spread

        # Corps en feu - forme plus agressive
        body_points = []
        for i in range(20):
            angle = (2 * math.pi / 20) * i
            distortion = math.sin(self.rebirth_pulse * 0.15 + i * 0.5) * 8
            rx = 38 + distortion
            ry = 48 + distortion * 0.5
            bx = center + math.cos(angle) * rx
            by = center + math.sin(angle) * ry
            body_points.append((bx, by))

        # Corps incandescent
        pygame.draw.polygon(surf, (100, 30, 10), body_points)
        pygame.draw.polygon(surf, (255, 150, 50), body_points, 4)

        # Ailes en feu
        self._draw_wing(surf, center, -1, wing_amplitude)
        self._draw_wing(surf, center, 1, wing_amplitude)

        # Queue de feu intense
        self._draw_tail(surf, center)

        # Crete de flammes plus haute
        head_y = center - 35
        for i in range(7):
            flame_height = 25 + math.sin(self.flame_timer * 0.3 + i * 0.4) * 12
            flame_x = center + (i - 3) * 7
            color = (255, max(0, 200 - i * 30), 50)
            points = [
                (flame_x, head_y - 5),
                (flame_x - 5, head_y + flame_height),
                (flame_x + 5, head_y + flame_height)
            ]
            pygame.draw.polygon(surf, color, points)

        # Yeux en feu
        eye_intensity = abs(math.sin(self.rebirth_pulse * 0.2)) * 100
        left_eye = (center - 12, center - 20)
        right_eye = (center + 12, center - 20)

        for eye_pos in [left_eye, right_eye]:
            pygame.draw.circle(surf, (255, int(150 + eye_intensity), 50), eye_pos, 10)
            pygame.draw.circle(surf, (255, 255, 150), eye_pos, 6)
            pygame.draw.circle(surf, WHITE, eye_pos, 3)

        # Noyau de feu
        core_size = 22 + abs(math.sin(self.rebirth_pulse * 0.08)) * 8
        pygame.draw.circle(surf, (150, 50, 0), (center, center), int(core_size))
        pygame.draw.circle(surf, (255, 100, 0), (center, center), int(core_size * 0.75))
        pygame.draw.circle(surf, (255, 200, 100), (center, center), int(core_size * 0.5))
        pygame.draw.circle(surf, WHITE, (center, center), int(core_size * 0.25))

        # Lignes d'energie craquelees
        for i in range(8):
            angle = (2 * math.pi / 8) * i + self.rebirth_pulse * 0.02
            inner_r = 25
            outer_r = 45 + math.sin(self.rebirth_pulse * 0.1 + i) * 10
            start = (center + math.cos(angle) * inner_r, center + math.sin(angle) * inner_r)
            end = (center + math.cos(angle) * outer_r, center + math.sin(angle) * outer_r)
            pygame.draw.line(surf, (255, 200, 100), start, end, 2)

        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1
        self.flame_timer += 1
        self.wing_angle += self.wing_flap_speed
        self.core_pulse += 1
        self.glow_intensity = abs(math.sin(self.pulse_timer * 0.04)) * 80

        # Activer le mode renaissance a 35% HP
        if self.hp <= self.max_hp * 0.35 and not self.rebirth_mode and not self.rebirth_transition:
            self.rebirth_transition = True
            self.rebirth_transition_timer = 0
            self.rebirth_flash_alpha = 0
            print("Boss 9: TRANSITION RENAISSANCE...")

        # Animation de transition
        if self.rebirth_transition:
            self.rebirth_transition_timer += 1
            progress = self.rebirth_transition_timer / self.rebirth_transition_duration

            # Flash blanc croissant puis decroissant
            if progress < 0.5:
                self.rebirth_flash_alpha = int(255 * (progress * 2))
            else:
                self.rebirth_flash_alpha = int(255 * (1 - (progress - 0.5) * 2))

            # Vibration du boss
            if self.rebirth_transition_timer % 4 < 2:
                self.rect.x += random.randint(-3, 3)
                self.rect.y += random.randint(-2, 2)

            if self.rebirth_transition_timer >= self.rebirth_transition_duration:
                self.rebirth_transition = False
                self.rebirth_mode = True
                self.shoot_delay_frames = 8
                self.wing_flap_speed = 0.12
                print("Boss 9: MODE RENAISSANCE ACTIVE!")

        if self.rebirth_mode:
            self.rebirth_pulse += 5

        # Spawn de plumes
        self.feather_spawn_timer += 1
        if self.feather_spawn_timer >= self.feather_spawn_interval:
            self.feather_spawn_timer = 0
            self._spawn_feather()

        # Update des plumes tombantes
        for feather in self.falling_feathers[:]:
            feather['y'] += feather['speed']
            feather['x'] += math.sin(feather['angle']) * 2
            feather['angle'] += feather['rotation']
            if feather['y'] > 700:
                self.falling_feathers.remove(feather)

        # Update des particules void
        for particle in self.void_particles[:]:
            particle['life'] -= 1
            particle['y'] += particle['dy']
            particle['x'] += particle['dx']
            particle['size'] *= 0.95
            if particle['life'] <= 0 or particle['size'] < 1:
                self.void_particles.remove(particle)

        # Spawn nouvelles particules
        if len(self.void_particles) < self.max_particles and random.random() < 0.3:
            self._spawn_void_particle()

        # Update des flammes spectrales
        for flame in self.spectral_flames:
            flame['angle'] += flame['speed']
            flame['height'] = 20 + 20 * abs(math.sin(self.timer * 0.1 + flame['phase']))

        # Update des ondes de cri
        for wave in self.screech_waves[:]:
            wave['radius'] += 8
            wave['alpha'] -= 5
            if wave['alpha'] <= 0:
                self.screech_waves.remove(wave)

        # Animation de mort
        if self.is_dying:
            self.death_animation_timer += 1
            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 3) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_rebirth_sprite() if self.rebirth_mode else self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(1, int(4 * (1 - progress * 0.98)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(-30, self.size + 30)
                rand_y = self.rect.top + random.randint(-30, self.size + 30)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=900))

            for exp in self.death_explosions:
                exp.update()
            self.death_explosions = [exp for exp in self.death_explosions if not exp.is_finished()]

            if self.death_animation_timer >= self.death_animation_duration:
                return True
            return False

        # Animation de degats
        if self.damage_animation_active:
            self.damage_animation_timer += 1
            if (self.damage_animation_timer // self.damage_flash_interval) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_rebirth_sprite() if self.rebirth_mode else self._create_boss_sprite()

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self._create_rebirth_sprite() if self.rebirth_mode else self._create_boss_sprite()
        else:
            self.image = self._create_rebirth_sprite() if self.rebirth_mode else self._create_boss_sprite()

        # Mouvement d'entree
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 9 en position de combat!")
        else:
            # Mouvement fluide en forme de 8
            move_x = math.sin(self.timer * 0.02) * 5 + math.cos(self.timer * 0.015) * 3
            move_y = math.sin(self.timer * 0.025) * math.cos(self.timer * 0.015) * 4
            self.rect.x += int(move_x)
            self.rect.y = self.target_y + int(move_y * 10)

            self.rect.x = max(130, min(SCREEN_WIDTH - 130, self.rect.x))

            # Patterns de tir
            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    num_patterns = 9 if self.rebirth_mode else 6
                    pattern_index = (self.timer // self.pattern_switch_interval) % num_patterns
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def _spawn_feather(self):
        """Fait apparaitre une plume qui tombe"""
        side = random.choice([-1, 1])
        feather = {
            'x': self.rect.centerx + side * random.randint(30, 80),
            'y': self.rect.centery,
            'speed': random.uniform(1, 3),
            'angle': random.uniform(0, 2 * math.pi),
            'rotation': random.uniform(-0.1, 0.1),
            'size': random.randint(8, 15),
            'color': (150, 80, 200) if not self.rebirth_mode else (255, 150, 50)
        }
        self.falling_feathers.append(feather)

    def _spawn_void_particle(self):
        """Fait apparaitre une particule void"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        particle = {
            'x': self.rect.centerx + random.randint(-40, 40),
            'y': self.rect.centery + random.randint(-40, 40),
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed - 1,  # Monte legerement
            'size': random.randint(3, 8),
            'life': random.randint(30, 60),
            'color': (180, 100, 255) if not self.rebirth_mode else (255, 180, 80)
        }
        self.void_particles.append(particle)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns du Void Phoenix"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 50

        if pattern_index == 0:
            # Pluie de plumes void
            for i in range(9):
                offset_x = (i - 4) * 40
                angle_offset = math.sin(self.timer * 0.05 + i * 0.4) * 0.3
                projectiles.append(VoidFeatherProjectile(bx + offset_x, by, angle_offset, 1, speed=5))
            print("Boss 9: Pluie de plumes!")

        elif pattern_index == 1:
            # Flammes de l'ame - tirs en eventail
            for angle_deg in [-60, -40, -20, 0, 20, 40, 60]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(SoulFireProjectile(bx, by, dx, dy, speed=6))
            print("Boss 9: Flammes de l'ame!")

        elif pattern_index == 2:
            # Orbes d'annihilation - gros projectiles lents
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(AnnihilationOrbProjectile(bx, by, dx, dy, speed=3))
            projectiles.append(AnnihilationOrbProjectile(bx - 50, by, dx - 0.2, dy, speed=3))
            projectiles.append(AnnihilationOrbProjectile(bx + 50, by, dx + 0.2, dy, speed=3))
            print("Boss 9: Orbes d'annihilation!")

        elif pattern_index == 3:
            # Spirale de feu void
            for i in range(10):
                angle = math.radians(self.timer * 4 + i * 36)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss9Projectile(bx, by, dx, dy, speed=5))
            print("Boss 9: Spirale void!")

        elif pattern_index == 4:
            # Vagues de phoenix
            projectiles.append(PhoenixWaveProjectile(bx, by, speed=4))
            print("Boss 9: Vague phoenix!")

        elif pattern_index == 5:
            # Barrage de plumes depuis les ailes
            for side in [-1, 1]:
                wing_x = bx + side * 60
                for i in range(5):
                    angle = math.radians(90 + side * (20 + i * 15))
                    dx = math.cos(angle) * side
                    dy = math.sin(angle)
                    projectiles.append(VoidFeatherProjectile(wing_x, by - 30, dx, abs(dy), speed=6))
            print("Boss 9: Barrage d'ailes!")

        # Patterns du mode renaissance
        elif pattern_index == 6 and self.rebirth_mode:
            # Explosion de flammes dans toutes les directions
            for i in range(20):
                angle = (2 * math.pi / 20) * i + self.timer * 0.05
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(SoulFireProjectile(bx, by, dx, dy, speed=6))
            print("Boss 9: EXPLOSION DE RENAISSANCE!")

        elif pattern_index == 7 and self.rebirth_mode:
            # Double spirale inversee
            for i in range(8):
                angle1 = math.radians(self.timer * 5 + i * 45)
                angle2 = math.radians(-self.timer * 5 + i * 45 + 22.5)
                projectiles.append(Boss9Projectile(bx, by, math.cos(angle1), math.sin(angle1), speed=5))
                projectiles.append(SoulFireProjectile(bx, by, math.cos(angle2), math.sin(angle2), speed=5))
            print("Boss 9: DOUBLE SPIRALE!")

        elif pattern_index == 8 and self.rebirth_mode:
            # Apocalypse - tous les types combines
            # Vague centrale
            projectiles.append(PhoenixWaveProjectile(bx, by, speed=3))
            # Orbe principal
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(AnnihilationOrbProjectile(bx, by, dx, dy, speed=4))
            # Plumes laterales
            for i in range(6):
                angle = math.radians(self.timer * 3 + i * 60)
                projectiles.append(VoidFeatherProjectile(bx, by, math.cos(angle), math.sin(angle), speed=5))
            print("Boss 9: APOCALYPSE!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des degats au boss"""
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

        # Cri du phoenix quand il prend des degats
        if random.random() < 0.3:
            self.screech_waves.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'radius': 30,
                'alpha': 150
            })

    def draw(self, surface):
        # Aura void/feu
        if not self.is_dying:
            pulse = abs(math.sin(self.pulse_timer * 0.03)) * 0.5 + 0.5

            if self.rebirth_mode:
                aura_color = (150, 80, 20, int(60 * pulse))
            else:
                aura_color = (80, 30, 120, int(50 * pulse))

            aura_size = int(130 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color, (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            # Dessiner les flammes spectrales autour du boss
            for flame in self.spectral_flames:
                fx = self.rect.centerx + math.cos(flame['angle']) * flame['radius']
                fy = self.rect.centery + math.sin(flame['angle']) * flame['radius']

                if self.rebirth_mode:
                    flame_colors = [(255, 200, 100), (255, 150, 50), (255, 100, 0)]
                else:
                    flame_colors = [(180, 100, 255), (120, 50, 200), (80, 30, 150)]

                for idx, color in enumerate(flame_colors):
                    height = flame['height'] - idx * 8
                    if height > 0:
                        points = [
                            (fx, fy - height // 2),
                            (fx - 5 + idx * 2, fy + height // 2),
                            (fx + 5 - idx * 2, fy + height // 2)
                        ]
                        pygame.draw.polygon(surface, color, points)

            # Particules void
            for particle in self.void_particles:
                alpha = int(255 * (particle['life'] / 60))
                p_surf = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
                p_color = (*particle['color'], alpha)
                pygame.draw.circle(p_surf, p_color, (int(particle['size']), int(particle['size'])), int(particle['size']))
                surface.blit(p_surf, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

            # Plumes tombantes
            for feather in self.falling_feathers:
                # Dessiner une forme de plume simple
                f_surf = pygame.Surface((feather['size'] * 2, feather['size'] * 3), pygame.SRCALPHA)
                points = [
                    (feather['size'], 0),
                    (feather['size'] * 2, feather['size'] * 2),
                    (feather['size'], feather['size'] * 3),
                    (0, feather['size'] * 2)
                ]
                pygame.draw.polygon(f_surf, feather['color'], points)
                pygame.draw.polygon(f_surf, WHITE, points, 1)
                rotated = pygame.transform.rotate(f_surf, math.degrees(feather['angle']))
                surface.blit(rotated, (int(feather['x']) - rotated.get_width() // 2,
                                       int(feather['y']) - rotated.get_height() // 2))

            # Ondes de cri
            for wave in self.screech_waves:
                wave_surf = pygame.Surface((wave['radius'] * 2 + 10, wave['radius'] * 2 + 10), pygame.SRCALPHA)
                color = (200, 100, 255, wave['alpha']) if not self.rebirth_mode else (255, 150, 100, wave['alpha'])
                pygame.draw.circle(wave_surf, color, (wave['radius'] + 5, wave['radius'] + 5), wave['radius'], 3)
                surface.blit(wave_surf, (wave['x'] - wave['radius'] - 5, wave['y'] - wave['radius'] - 5))

        # Flash de transition renaissance
        if self.rebirth_transition and self.rebirth_flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, 800), pygame.SRCALPHA)
            flash_surf.fill((255, 200, 100, self.rebirth_flash_alpha))
            surface.blit(flash_surf, (0, 0))

        # Dessiner le boss
        surface.blit(self.image, self.rect)

        # Indicateur de mode renaissance
        if self.rebirth_mode:
            rage_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.15)))
            rage_surf = pygame.Surface((140, 28), pygame.SRCALPHA)
            pygame.draw.rect(rage_surf, (255, 120, 50, rage_alpha), (0, 0, 140, 28))
            surface.blit(rage_surf, (self.rect.centerx - 70, self.rect.top - 40))

        # Explosions de mort
        for exp in self.death_explosions:
            exp.draw(surface)
