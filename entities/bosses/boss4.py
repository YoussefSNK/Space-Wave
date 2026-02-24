import random
import math

from config import SCREEN_WIDTH
from graphics.effects import Explosion
from entities.enemy import Enemy
from entities.projectiles import Boss4Projectile, BouncingProjectile, SplittingProjectile
from entities.bosses.boss4_sprite import Boss4Sprite


class Boss4(Enemy):
    """Quatrieme Boss - Boss final ultime avec des patterns complexes"""
    def __init__(self, x, y, speed=2, target_y=80):
        super().__init__(x, y, speed)

        self.size = 160
        self.sprite_renderer = Boss4Sprite(self.size)
        self.image = self.sprite_renderer.create_sprite()
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

        self.cycle_count = 0
        self.last_pattern_index = -1

        self.branch_stretch_active = False
        self.branch_stretch_timer = 0
        self.branch_stretch_phase = 0  # 0=annonce, 1=etendre, 2=tourner, 3=replier
        self.branch_stretch_cycle = 0  # 0-9 (10 cycles)
        self.branch_stretch_rotation = 0
        self.branch_stretch_direction = 1
        self.branch_stretch_factor = 1
        self.branch_stretch_consecutive = 0  # nombre de fois consecutives dans le meme sens
        self.branch_announce_duration = 20

        self.branch_windup_active = False
        self.branch_windup_phase = 0  # 0=centrage, 1=etendre1, 2=replier1, 3=pause1, 4=etendre2, 5=replier2, 6=pause2
        self.branch_windup_timer = 0
        self.branch_windup_factor = 1.0
        self.branch_extend_duration = 30
        self.branch_rotate_duration = 30
        self.branch_retract_duration = 30

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
        return self.sprite_renderer.create_sprite()

    def _create_damaged_sprite(self):
        return self.sprite_renderer.create_damaged_sprite()

    def _create_shield_sprite(self):
        return self.sprite_renderer.create_shield_sprite()

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
            if not self.branch_windup_active:
                self.movement_angle += 0.005 if self.branch_stretch_active else 0.02
                offset_x = math.sin(self.movement_angle) * self.movement_radius_x
                offset_y = math.sin(self.movement_angle * 2) * self.movement_radius_y
                self.rect.centerx = SCREEN_WIDTH // 2 + int(offset_x)
                self.rect.centery = self.target_y + int(offset_y)

            if self.hp < 25 and not self.shield_active and self.timer - self.last_shield_time >= self.shield_cooldown:
                self.shield_active = True
                self.shield_timer = 0
                print("Boss 4: Bouclier active!")

            if self.branch_windup_active:
                if self.branch_windup_phase == 0:
                    # Centrage vers le milieu de l'ecran
                    diff_x = SCREEN_WIDTH // 2 - self.rect.centerx
                    diff_y = self.target_y - self.rect.centery
                    speed = 5
                    if abs(diff_x) <= speed and abs(diff_y) <= speed:
                        self.rect.centerx = SCREEN_WIDTH // 2
                        self.rect.centery = self.target_y
                        self.branch_windup_phase = 1
                        self.branch_windup_timer = 0
                        self.branch_windup_factor = 1.0
                    else:
                        self.rect.centerx += speed if diff_x > 0 else -speed if abs(diff_x) > speed else diff_x
                        self.rect.centery += speed if diff_y > 0 else -speed if abs(diff_y) > speed else diff_y
                elif self.branch_windup_phase == 1:
                    # Etendre a 20% du max (factor ~7)
                    self.branch_windup_timer += 1
                    progress = self.branch_windup_timer / 10
                    self.branch_windup_factor = 1 + progress * 6
                    if self.branch_windup_timer >= 10:
                        self.branch_windup_factor = 7
                        self.branch_windup_phase = 2
                        self.branch_windup_timer = 0
                elif self.branch_windup_phase == 2:
                    # Replier depuis 20%
                    self.branch_windup_timer += 1
                    progress = self.branch_windup_timer / 7
                    self.branch_windup_factor = 7 - progress * 6
                    if self.branch_windup_timer >= 7:
                        self.branch_windup_factor = 1
                        self.branch_windup_phase = 3
                        self.branch_windup_timer = 0
                elif self.branch_windup_phase == 3:
                    # Pause entre les deux etirements
                    self.branch_windup_timer += 1
                    if self.branch_windup_timer >= 15:
                        self.branch_windup_phase = 4
                        self.branch_windup_timer = 0
                elif self.branch_windup_phase == 4:
                    # Etendre a 50% du max (factor ~15)
                    self.branch_windup_timer += 1
                    progress = self.branch_windup_timer / 12
                    self.branch_windup_factor = 1 + progress * 14
                    if self.branch_windup_timer >= 12:
                        self.branch_windup_factor = 15
                        self.branch_windup_phase = 5
                        self.branch_windup_timer = 0
                elif self.branch_windup_phase == 5:
                    # Replier depuis 50%
                    self.branch_windup_timer += 1
                    progress = self.branch_windup_timer / 8
                    self.branch_windup_factor = 15 - progress * 14
                    if self.branch_windup_timer >= 8:
                        self.branch_windup_factor = 1
                        self.branch_windup_phase = 6
                        self.branch_windup_timer = 0
                elif self.branch_windup_phase == 6:
                    # Pause avant le pattern
                    self.branch_windup_timer += 1
                    if self.branch_windup_timer >= 15:
                        # Wind-up termine : lancer le vrai pattern
                        self.branch_windup_active = False
                        self.branch_windup_factor = 1.0
                        self.movement_angle = 0.0  # resynchroniser depuis le centre
                        self.branch_stretch_active = True
                        self.branch_stretch_timer = 0
                        self.branch_stretch_phase = 0
                        self.branch_stretch_cycle = 0
                        self.branch_stretch_rotation = 0
                        self.branch_stretch_factor = 1
                        self.branch_stretch_direction = random.choice([-1, 1])
                        self.branch_stretch_consecutive = 1
                return False

            if self.branch_stretch_active:
                self.branch_stretch_timer += 1
                if self.branch_stretch_phase >= 1:
                    if self.branch_stretch_phase == 1:
                        self.branch_stretch_rotation -= 0.05 * self.branch_stretch_direction
                    else:
                        self.branch_stretch_rotation -= 0.75 * self.branch_stretch_direction
                if self.branch_stretch_phase == 0:
                    # Phase annonce
                    if self.branch_stretch_timer >= self.branch_announce_duration:
                        self.branch_stretch_timer = 0
                        self.branch_stretch_phase = 1
                elif self.branch_stretch_phase == 1:
                    # Phase etendre
                    progress = self.branch_stretch_timer / self.branch_extend_duration
                    self.branch_stretch_factor = 1 + progress * 29
                    if self.branch_stretch_timer >= self.branch_extend_duration:
                        self.branch_stretch_factor = 30
                        self.branch_stretch_timer = 0
                        self.branch_stretch_phase = 2
                elif self.branch_stretch_phase == 2:
                    # Phase rotation (branches etendues)
                    if self.branch_stretch_timer >= self.branch_rotate_duration:
                        self.branch_stretch_timer = 0
                        self.branch_stretch_phase = 3
                elif self.branch_stretch_phase == 3:
                    # Phase replier
                    progress = self.branch_stretch_timer / self.branch_retract_duration
                    self.branch_stretch_factor = 30 - progress * 29
                    if self.branch_stretch_timer >= self.branch_retract_duration:
                        self.branch_stretch_factor = 1
                        self.branch_stretch_timer = 0
                        self.branch_stretch_cycle += 1
                        if self.branch_stretch_cycle >= 10:
                            self.branch_stretch_active = False
                            self.branch_stretch_cycle = 0
                            self.branch_stretch_rotation = 0
                            self.branch_stretch_factor = 1
                        else:
                            self.branch_stretch_phase = 0
                            if self.branch_stretch_consecutive >= 2:
                                new_dir = -self.branch_stretch_direction
                                self.branch_stretch_consecutive = 1
                            else:
                                new_dir = random.choice([-1, 1])
                                if new_dir == self.branch_stretch_direction:
                                    self.branch_stretch_consecutive += 1
                                else:
                                    self.branch_stretch_consecutive = 1
                            self.branch_stretch_direction = new_dir
                return False

            if player_position and enemy_projectiles is not None:
                if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                    self.last_shot_frame = self.timer
                    pattern_index = (self.timer // self.pattern_switch_interval) % 7
                    if pattern_index == 0 and self.last_pattern_index == 6:
                        self.cycle_count += 1
                    self.last_pattern_index = pattern_index
                    if pattern_index == 2 and self.cycle_count >= 1 and not self.branch_stretch_active and not self.branch_windup_active:
                        self.branch_windup_active = True
                        self.branch_windup_phase = 0
                        self.branch_windup_timer = 0
                        self.branch_windup_factor = 1.0
                        print("Boss 4: Wind-up!")
                        return False
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
            self.sprite_renderer.draw_aura(surface, cx, cy, pulse)
            self.sprite_renderer.draw_rings(surface, cx, cy, self.ring_rotation)
            self.sprite_renderer.draw_orbs(surface, cx, cy, self.ring_rotation)

        if self.branch_windup_active:
            if self.branch_windup_phase == 0:
                surface.blit(self.image, self.rect)
            else:
                self.sprite_renderer.draw_stretched_branches(
                    surface, cx, cy, self.branch_windup_factor, 0, 1.0)
        elif self.branch_stretch_active:
            if self.branch_stretch_phase == 0:
                progress = self.branch_stretch_timer / self.branch_announce_duration
                self.sprite_renderer.draw_ghost_branches(
                    surface, cx, cy, self.branch_stretch_rotation, progress)
                self.sprite_renderer.draw_rotation_announcement(
                    surface, cx, cy, self.branch_stretch_direction, progress)
            orange_fade = max(0, 1.0 - ((self.branch_stretch_factor - 1) / 29) * 5)
            self.sprite_renderer.draw_stretched_branches(
                surface, cx, cy, self.branch_stretch_factor,
                self.branch_stretch_rotation, orange_fade)
        else:
            surface.blit(self.image, self.rect)

        if self.charging and (self.swoop_phase == 0 or self.swoop_phase == 1):
            self.sprite_renderer.draw_swoop_warning(
                surface, cx, cy, self.charge_timer,
                self.charge_warning_duration, self.swoop_phase, self.target_y)

        for exp in self.death_explosions:
            exp.draw(surface)
