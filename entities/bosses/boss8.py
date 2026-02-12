import pygame
import random
import math

from config import SCREEN_WIDTH, WHITE
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss8Projectile, PrismBeamProjectile, CrystalShardProjectile, ReflectingProjectile


class Boss8(Enemy):
    """Huitieme Boss - Le Leviathan Cristallin avec des effets prismatiques"""
    def __init__(self, x, y, speed=2, target_y=100):
        super().__init__(x, y, speed)

        self.size = 200
        self.hp = 90
        self.max_hp = 90
        self.target_y = target_y
        self.in_position = False
        self.timer = 0
        self.shoot_delay_frames = 12
        self.last_shot_frame = 0
        self.current_pattern = 0
        self.pattern_switch_interval = 180

        # Animation de rotation des cristaux (doit etre initialise AVANT _create_boss_sprite)
        self.crystal_rotation = 0
        self.inner_rotation = 0
        self.color_cycle = 0

        # Creer le sprite apres l'initialisation des variables de rotation
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(x, y))

        # Fragments orbitaux
        self.orbital_fragments = []
        self.num_fragments = 8
        self.fragment_orbit_radius = 85
        self.fragment_orbit_speed = 0.02
        for i in range(self.num_fragments):
            angle = (2 * math.pi / self.num_fragments) * i
            self.orbital_fragments.append({
                'angle': angle,
                'radius': self.fragment_orbit_radius + random.randint(-10, 10),
                'size': random.randint(8, 14),
                'color_offset': random.uniform(0, 2 * math.pi),
                'active': True
            })

        # Mode brisé (shattered)
        self.shattered_mode = False
        self.shatter_pulse = 0
        self.crack_lines = []
        self._generate_crack_lines()

        # Effet prismatique
        self.prism_timer = 0

        # Animation de dégâts
        self.damage_animation_active = False
        self.damage_animation_duration = 12
        self.damage_animation_timer = 0
        self.damage_flash_interval = 2

        # Animation de mort
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 400
        self.death_explosion_timer = 0
        self.death_explosions = []

        # Bouclier cristallin
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 180
        self.shield_cooldown = 0
        self.shield_max_cooldown = 300

        # Rayons prismatiques
        self.beam_charging = False
        self.beam_charge_timer = 0
        self.beam_charge_duration = 60

        self.pulse_timer = 0
        self.glow_intensity = 0

    def _generate_crack_lines(self):
        """Génère les lignes de fissure pour le mode brisé"""
        center = self.size // 2
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(30, 70)
            start_dist = random.randint(10, 30)
            self.crack_lines.append({
                'angle': angle,
                'start': start_dist,
                'length': length,
                'offset': random.uniform(0, math.pi)
            })

    def _get_rainbow_color(self, offset=0):
        """Retourne une couleur arc-en-ciel basée sur le timer"""
        hue = (self.color_cycle + offset) % (2 * math.pi)
        # Conversion HSV vers RGB simplifiée
        r = int(127 + 127 * math.sin(hue))
        g = int(127 + 127 * math.sin(hue + 2 * math.pi / 3))
        b = int(127 + 127 * math.sin(hue + 4 * math.pi / 3))
        return (r, g, b)

    def _create_boss_sprite(self):
        """Crée un sprite procédural pour le Boss 8 - Léviathan Cristallin"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Corps cristallin principal - forme hexagonale
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30) + self.crystal_rotation * 0.01
            hx = center + math.cos(angle) * 55
            hy = center + math.sin(angle) * 55
            hex_points.append((hx, hy))

        # Dégradé du corps principal
        pygame.draw.polygon(surf, (40, 80, 120), hex_points)

        # Hexagone intérieur plus clair
        inner_hex = []
        for i in range(6):
            angle = math.radians(60 * i - 30) + self.crystal_rotation * 0.01
            hx = center + math.cos(angle) * 40
            hy = center + math.sin(angle) * 40
            inner_hex.append((hx, hy))
        pygame.draw.polygon(surf, (80, 140, 180), inner_hex)

        # Contour lumineux
        pygame.draw.polygon(surf, (150, 200, 255), hex_points, 3)

        # Cristaux externes (8 pointes)
        for i in range(8):
            base_angle = math.radians(45 * i) + self.crystal_rotation * 0.02

            # Pointe principale du cristal
            tip_x = center + math.cos(base_angle) * 80
            tip_y = center + math.sin(base_angle) * 80

            # Base du cristal (deux points)
            left_angle = base_angle - 0.3
            right_angle = base_angle + 0.3
            base_dist = 45

            left_x = center + math.cos(left_angle) * base_dist
            left_y = center + math.sin(left_angle) * base_dist
            right_x = center + math.cos(right_angle) * base_dist
            right_y = center + math.sin(right_angle) * base_dist

            # Couleur prismatique
            color = self._get_rainbow_color(i * 0.8)
            darker_color = (color[0] // 2, color[1] // 2, color[2] // 2)

            # Dessiner le cristal (triangle)
            crystal_points = [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
            pygame.draw.polygon(surf, darker_color, crystal_points)
            pygame.draw.polygon(surf, color, crystal_points, 2)

            # Reflet sur le cristal
            mid_x = (tip_x + left_x) / 2
            mid_y = (tip_y + left_y) / 2
            pygame.draw.line(surf, (255, 255, 255, 150),
                           (int(mid_x), int(mid_y)),
                           (int(tip_x), int(tip_y)), 1)

        # Noyau central brillant
        core_color = self._get_rainbow_color()
        pygame.draw.circle(surf, (20, 40, 60), (center, center), 25)
        pygame.draw.circle(surf, core_color, (center, center), 20)
        pygame.draw.circle(surf, (200, 220, 255), (center, center), 12)
        pygame.draw.circle(surf, WHITE, (center, center), 6)

        # Triangles intérieurs (motif géométrique)
        for i in range(6):
            angle1 = math.radians(60 * i) + self.inner_rotation * 0.03
            angle2 = math.radians(60 * (i + 1)) + self.inner_rotation * 0.03
            x1 = center + math.cos(angle1) * 30
            y1 = center + math.sin(angle1) * 30
            x2 = center + math.cos(angle2) * 30
            y2 = center + math.sin(angle2) * 30
            pygame.draw.line(surf, (100, 180, 255, 150), (center, center), (int(x1), int(y1)), 1)
            pygame.draw.line(surf, (100, 180, 255, 150), (int(x1), int(y1)), (int(x2), int(y2)), 1)

        return surf

    def _create_damaged_sprite(self):
        """Crée un sprite endommagé avec flash blanc"""
        surf = self._create_boss_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 200))
        surf.blit(flash, (0, 0))
        return surf

    def _create_shattered_sprite(self):
        """Crée un sprite en mode brisé avec fissures et couleurs intenses"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        # Corps fissuré - hexagone déformé
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30) + self.crystal_rotation * 0.02
            distortion = math.sin(self.shatter_pulse * 0.1 + i) * 5
            hx = center + math.cos(angle) * (55 + distortion)
            hy = center + math.sin(angle) * (55 + distortion)
            hex_points.append((hx, hy))

        # Couleurs plus intenses/rougeâtres en mode shattered
        pygame.draw.polygon(surf, (100, 40, 60), hex_points)

        inner_hex = []
        for i in range(6):
            angle = math.radians(60 * i - 30) + self.crystal_rotation * 0.02
            hx = center + math.cos(angle) * 40
            hy = center + math.sin(angle) * 40
            inner_hex.append((hx, hy))
        pygame.draw.polygon(surf, (180, 80, 100), inner_hex)
        pygame.draw.polygon(surf, (255, 100, 150), hex_points, 3)

        # Cristaux externes en mode rage (rouges/oranges)
        for i in range(8):
            base_angle = math.radians(45 * i) + self.crystal_rotation * 0.03 + self.shatter_pulse * 0.05
            wobble = math.sin(self.shatter_pulse * 0.15 + i) * 3

            tip_x = center + math.cos(base_angle) * (85 + wobble)
            tip_y = center + math.sin(base_angle) * (85 + wobble)

            left_angle = base_angle - 0.3
            right_angle = base_angle + 0.3
            base_dist = 45

            left_x = center + math.cos(left_angle) * base_dist
            left_y = center + math.sin(left_angle) * base_dist
            right_x = center + math.cos(right_angle) * base_dist
            right_y = center + math.sin(right_angle) * base_dist

            # Couleurs chaudes pour le mode shattered
            intensity = int(200 + 55 * math.sin(self.shatter_pulse * 0.1 + i))
            color = (intensity, int(intensity * 0.3), 0)
            darker_color = (color[0] // 2, color[1] // 2, 0)

            crystal_points = [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
            pygame.draw.polygon(surf, darker_color, crystal_points)
            pygame.draw.polygon(surf, color, crystal_points, 2)

        # Fissures brillantes
        for crack in self.crack_lines:
            glow = abs(math.sin(self.shatter_pulse * 0.08 + crack['offset']))
            crack_color = (255, int(100 + 155 * glow), int(50 * glow))

            start_x = center + math.cos(crack['angle']) * crack['start']
            start_y = center + math.sin(crack['angle']) * crack['start']
            end_x = center + math.cos(crack['angle']) * (crack['start'] + crack['length'])
            end_y = center + math.sin(crack['angle']) * (crack['start'] + crack['length'])

            pygame.draw.line(surf, crack_color,
                           (int(start_x), int(start_y)),
                           (int(end_x), int(end_y)), 2)

        # Noyau instable
        core_pulse = abs(math.sin(self.shatter_pulse * 0.15)) * 5
        pygame.draw.circle(surf, (60, 20, 30), (center, center), int(25 + core_pulse))
        pygame.draw.circle(surf, (255, 100, 50), (center, center), int(20 + core_pulse))
        pygame.draw.circle(surf, (255, 200, 150), (center, center), int(12 + core_pulse * 0.5))
        pygame.draw.circle(surf, WHITE, (center, center), 6)

        return surf

    def update(self, player_position=None, enemy_projectiles=None):
        self.timer += 1
        self.pulse_timer += 1
        self.prism_timer += 1
        self.color_cycle += 0.03
        self.crystal_rotation += 1
        self.inner_rotation += 2
        self.glow_intensity = abs(math.sin(self.pulse_timer * 0.04)) * 60

        # Activer le mode shattered à 25% HP
        if self.hp <= self.max_hp * 0.25 and not self.shattered_mode:
            self.shattered_mode = True
            self.shoot_delay_frames = 7
            print("Boss 8: MODE SHATTERED ACTIVE!")

        if self.shattered_mode:
            self.shatter_pulse += 4

        # Gestion du bouclier
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        if self.shield_active:
            self.shield_timer += 1
            if self.shield_timer >= self.shield_duration:
                self.shield_active = False
                self.shield_timer = 0
                self.shield_cooldown = self.shield_max_cooldown

        # Animation de mort
        if self.is_dying:
            self.death_animation_timer += 1
            progress = self.death_animation_timer / self.death_animation_duration

            if (self.death_animation_timer // 2) % 2 == 0:
                self.image = self._create_damaged_sprite()
            else:
                self.image = self._create_shattered_sprite() if self.shattered_mode else self._create_boss_sprite()

            self.death_explosion_timer += 1
            explosion_interval = max(1, int(5 * (1 - progress * 0.98)))
            if self.death_explosion_timer >= explosion_interval:
                self.death_explosion_timer = 0
                rand_x = self.rect.left + random.randint(-30, self.size + 30)
                rand_y = self.rect.top + random.randint(-30, self.size + 30)
                self.death_explosions.append(Explosion(rand_x, rand_y, duration=800))

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
                self.image = self._create_shattered_sprite() if self.shattered_mode else self._create_boss_sprite()

            if self.damage_animation_timer >= self.damage_animation_duration:
                self.damage_animation_active = False
                self.damage_animation_timer = 0
                self.image = self._create_shattered_sprite() if self.shattered_mode else self._create_boss_sprite()
        else:
            self.image = self._create_shattered_sprite() if self.shattered_mode else self._create_boss_sprite()

        # Mise à jour des fragments orbitaux
        for fragment in self.orbital_fragments:
            if fragment['active']:
                fragment['angle'] += self.fragment_orbit_speed * (1.5 if self.shattered_mode else 1)

        # Mouvement d'entrée
        if not self.in_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.in_position = True
                print("Boss 8 en position de combat!")
        else:
            # Mouvement fluide et complexe
            move_x = math.sin(self.timer * 0.025) * 4 + math.cos(self.timer * 0.018) * 2
            move_y = math.cos(self.timer * 0.02) * 3
            self.rect.x += int(move_x)
            self.rect.y = self.target_y + int(math.sin(self.timer * 0.012) * 35)

            self.rect.x = max(120, min(SCREEN_WIDTH - 120, self.rect.x))

            # Activation du bouclier
            if not self.shield_active and self.shield_cooldown == 0 and self.hp <= self.max_hp * 0.5:
                if random.random() < 0.002:  # Faible chance par frame
                    self.shield_active = True
                    self.shield_timer = 0
                    print("Boss 8: Bouclier cristallin activé!")

            # Patterns de tir
            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    num_patterns = 8 if self.shattered_mode else 6
                    pattern_index = (self.timer // self.pattern_switch_interval) % num_patterns
                    self.current_pattern = pattern_index
                    projectiles = self.shoot_pattern(pattern_index, player_position)
                    enemy_projectiles.extend(projectiles)

    def shoot_pattern(self, pattern_index, player_position):
        """Retourne une liste de projectiles - patterns cristallins du Boss 8"""
        projectiles = []
        bx = self.rect.centerx
        by = self.rect.bottom - 40

        if pattern_index == 0:
            # Pluie de cristaux
            for i in range(7):
                offset_x = (i - 3) * 45
                angle_offset = math.sin(self.timer * 0.05 + i * 0.5) * 0.3
                projectiles.append(CrystalShardProjectile(bx + offset_x, by, angle_offset, 1, speed=5))
            print("Boss 8: Pluie de cristaux!")

        elif pattern_index == 1:
            # Rayons prismatiques convergents
            for angle_deg in [-50, -25, 0, 25, 50]:
                angle_rad = math.radians(angle_deg)
                dx = math.sin(angle_rad)
                dy = math.cos(angle_rad)
                projectiles.append(PrismBeamProjectile(bx, by, dx, dy, speed=6))
            print("Boss 8: Rayons prismatiques!")

        elif pattern_index == 2:
            # Tirs réfléchissants
            px, py = player_position
            dx = px - bx
            dy = py - by
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
            projectiles.append(ReflectingProjectile(bx, by, dx, dy, speed=5, reflections=3))
            projectiles.append(ReflectingProjectile(bx - 40, by, dx - 0.2, dy, speed=5, reflections=2))
            projectiles.append(ReflectingProjectile(bx + 40, by, dx + 0.2, dy, speed=5, reflections=2))
            print("Boss 8: Tirs réfléchissants!")

        elif pattern_index == 3:
            # Spirale cristalline
            for i in range(8):
                angle = math.radians(self.timer * 3 + i * 45)
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(Boss8Projectile(bx, by, dx, dy, speed=4))
            print("Boss 8: Spirale cristalline!")

        elif pattern_index == 4:
            # Vague de fragments depuis les orbes orbitaux
            active_fragments = [f for f in self.orbital_fragments if f['active']]
            for fragment in active_fragments[:4]:
                fx = self.rect.centerx + math.cos(fragment['angle']) * fragment['radius']
                fy = self.rect.centery + math.sin(fragment['angle']) * fragment['radius']
                px, py = player_position
                dx = px - fx
                dy = py - fy
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    dx /= dist
                    dy /= dist
                projectiles.append(CrystalShardProjectile(fx, fy, dx, dy, speed=6))
            print("Boss 8: Fragments orbitaux!")

        elif pattern_index == 5:
            # Mur ondulant de cristaux
            for i in range(12):
                offset_x = (i - 5.5) * 35
                wave_offset = math.sin(i * 0.6 + self.timer * 0.08) * 0.4
                projectiles.append(Boss8Projectile(bx + offset_x, by, wave_offset, 1, speed=5))
            print("Boss 8: Mur cristallin!")

        # Patterns du mode shattered
        elif pattern_index == 6 and self.shattered_mode:
            # Explosion de fragments dans toutes les directions
            for i in range(16):
                angle = (2 * math.pi / 16) * i + self.timer * 0.08
                dx = math.cos(angle)
                dy = math.sin(angle)
                projectiles.append(CrystalShardProjectile(bx, by, dx, dy, speed=6))
            print("Boss 8: EXPLOSION CRISTALLINE!")

        elif pattern_index == 7 and self.shattered_mode:
            # Chaos total - mélange de tous les types
            projectiles.append(PrismBeamProjectile(bx, by, 0, 1, speed=7))
            projectiles.append(ReflectingProjectile(bx - 60, by, 0.2, 1, speed=5, reflections=2))
            projectiles.append(ReflectingProjectile(bx + 60, by, -0.2, 1, speed=5, reflections=2))
            for i in range(6):
                angle = math.radians(self.timer * 4 + i * 60)
                projectiles.append(CrystalShardProjectile(bx, by, math.cos(angle), math.sin(angle), speed=5))
            print("Boss 8: TEMPETE PRISMATIQUE!")

        return projectiles

    def take_damage(self, amount=1):
        """Applique des dégâts au boss"""
        if self.shield_active:
            print("Boss 8: Bouclier absorbe les dégâts!")
            return
        self.hp -= amount
        self.damage_animation_active = True
        self.damage_animation_timer = 0

    def draw(self, surface):
        # Aura prismatique
        if not self.is_dying:
            pulse = abs(math.sin(self.pulse_timer * 0.025)) * 0.5 + 0.5

            if self.shattered_mode:
                aura_color = (150, 50, 50, int(50 * pulse))
            else:
                # Aura arc-en-ciel
                r, g, b = self._get_rainbow_color()
                aura_color = (r // 3, g // 3, b // 3, int(40 * pulse))

            aura_size = int(110 * pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color, (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (self.rect.centerx - aura_size, self.rect.centery - aura_size))

            # Dessiner les fragments orbitaux
            for fragment in self.orbital_fragments:
                if fragment['active']:
                    fx = self.rect.centerx + math.cos(fragment['angle']) * fragment['radius']
                    fy = self.rect.centery + math.sin(fragment['angle']) * fragment['radius']

                    if self.shattered_mode:
                        frag_color = (255, int(100 + 100 * math.sin(self.shatter_pulse * 0.1 + fragment['color_offset'])), 50)
                    else:
                        frag_color = self._get_rainbow_color(fragment['color_offset'])

                    # Fragment principal
                    pygame.draw.circle(surface, frag_color, (int(fx), int(fy)), fragment['size'])
                    # Reflet
                    pygame.draw.circle(surface, WHITE, (int(fx - 2), int(fy - 2)), fragment['size'] // 3)

            # Effet de bouclier
            if self.shield_active:
                shield_pulse = abs(math.sin(self.shield_timer * 0.1)) * 0.3 + 0.7
                shield_alpha = int(100 * shield_pulse)
                shield_radius = int(100 + 10 * math.sin(self.shield_timer * 0.15))

                shield_surf = pygame.Surface((shield_radius * 2 + 20, shield_radius * 2 + 20), pygame.SRCALPHA)

                # Hexagone de bouclier
                hex_points = []
                for i in range(6):
                    angle = math.radians(60 * i + self.shield_timer * 2)
                    hx = shield_radius + 10 + math.cos(angle) * shield_radius
                    hy = shield_radius + 10 + math.sin(angle) * shield_radius
                    hex_points.append((hx, hy))

                pygame.draw.polygon(shield_surf, (100, 200, 255, shield_alpha // 2), hex_points)
                pygame.draw.polygon(shield_surf, (150, 230, 255, shield_alpha), hex_points, 3)

                surface.blit(shield_surf, (self.rect.centerx - shield_radius - 10,
                                          self.rect.centery - shield_radius - 10))

            # Particules lumineuses autour du boss
            for i in range(10):
                angle = math.radians(self.pulse_timer * 2 + i * 36)
                radius = 100 + math.sin(self.pulse_timer * 0.04 + i) * 25
                px = self.rect.centerx + math.cos(angle) * radius
                py = self.rect.centery + math.sin(angle) * radius * 0.7

                if self.shattered_mode:
                    color = (255, 150, 50)
                else:
                    color = self._get_rainbow_color(i * 0.6)

                pygame.draw.circle(surface, color, (int(px), int(py)), 4)
                pygame.draw.circle(surface, WHITE, (int(px), int(py)), 2)

        # Dessiner le boss
        surface.blit(self.image, self.rect)

        # Indicateur de mode shattered
        if self.shattered_mode:
            rage_alpha = int(150 + 100 * abs(math.sin(self.timer * 0.12)))
            rage_surf = pygame.Surface((120, 25), pygame.SRCALPHA)
            pygame.draw.rect(rage_surf, (255, 100, 50, rage_alpha), (0, 0, 120, 25))
            surface.blit(rage_surf, (self.rect.centerx - 60, self.rect.top - 35))

        # Explosions de mort
        for exp in self.death_explosions:
            exp.draw(surface)
