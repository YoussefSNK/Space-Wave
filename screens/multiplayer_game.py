"""Écran de jeu multijoueur utilisant les mêmes classes que le mode solo."""

import pygame
import math
import random
from screens.base import Screen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, CYAN, RED, YELLOW
from graphics.background import Background
from graphics.effects import Explosion
from entities.player import Player
from entities.enemy import Enemy, ShootingEnemy
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6
from entities.powerup import PowerUp
from entities.projectiles import (
    Projectile, EnemyProjectile, BossProjectile, Boss2Projectile, Boss3Projectile,
    Boss4Projectile, Boss5Projectile, Boss6Projectile, HomingProjectile,
    BouncingProjectile, SplittingProjectile, ZigZagProjectile, GravityProjectile,
    TeleportingProjectile, VortexProjectile, BlackHoleProjectile, MirrorProjectile,
    PulseWaveProjectile
)
from network.client import GameClient


class SyncedProjectile(Projectile):
    """Projectile du joueur qui maintient un trail pour le rendu."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 0

    def sync_position(self, x, y):
        """Met à jour la position et le trail."""
        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        self.rect.centerx = x
        self.rect.centery = y


# Mapping des types de projectiles vers leurs classes
PROJECTILE_CLASSES = {
    "EnemyProjectile": EnemyProjectile,
    "BossProjectile": BossProjectile,
    "Boss2Projectile": Boss2Projectile,
    "Boss3Projectile": Boss3Projectile,
    "Boss4Projectile": Boss4Projectile,
    "Boss5Projectile": Boss5Projectile,
    "Boss6Projectile": Boss6Projectile,
    "HomingProjectile": HomingProjectile,
    "BouncingProjectile": BouncingProjectile,
    "SplittingProjectile": SplittingProjectile,
    "ZigZagProjectile": ZigZagProjectile,
    "GravityProjectile": GravityProjectile,
    "TeleportingProjectile": TeleportingProjectile,
    "VortexProjectile": VortexProjectile,
    "BlackHoleProjectile": BlackHoleProjectile,
    "MirrorProjectile": MirrorProjectile,
    "PulseWaveProjectile": PulseWaveProjectile,
}


def create_synced_enemy_projectile(x, y, proj_type, radius=5):
    """Crée un projectile ennemi en utilisant la vraie classe."""
    proj_class = PROJECTILE_CLASSES.get(proj_type)

    if proj_class == BlackHoleProjectile:
        proj = proj_class(x, y)
        return proj
    elif proj_class == PulseWaveProjectile:
        proj = proj_class(x, y)
        return proj
    elif proj_class == VortexProjectile:
        proj = proj_class(x, y, x, y + 100)
        proj.launched = True
        return proj
    elif proj_class == HomingProjectile:
        proj = proj_class(x, y)
        return proj
    elif proj_class == ZigZagProjectile:
        proj = proj_class(x, y, 1)
        return proj
    elif proj_class == GravityProjectile:
        proj = proj_class(x, y, 0, 1)
        return proj
    elif proj_class == TeleportingProjectile:
        proj = proj_class(x, y, 0, 1)
        return proj
    elif proj_class:
        proj = proj_class(x, y, 0, 1)
        return proj
    else:
        return EnemyProjectile(x, y, 0, 1)


class SyncedEnemyProjectile:
    """Wrapper pour synchroniser un projectile ennemi avec le serveur."""
    def __init__(self, x, y, proj_type="EnemyProjectile", radius=5):
        self.proj_type = proj_type
        self.projectile = create_synced_enemy_projectile(x, y, proj_type, radius)
        self.timer = 0

    def sync_position(self, x, y, radius=None):
        """Met à jour la position et le trail."""
        self.timer += 1

        # Ajouter au trail
        if hasattr(self.projectile, 'trail'):
            self.projectile.trail.append(self.projectile.rect.center)
            max_trail = getattr(self.projectile, 'max_trail_length', 5)
            if len(self.projectile.trail) > max_trail:
                self.projectile.trail.pop(0)

        # Mettre à jour la position
        self.projectile.rect.centerx = x
        self.projectile.rect.centery = y

        # Mettre à jour le radius pour certains projectiles
        if radius is not None and hasattr(self.projectile, 'radius'):
            self.projectile.radius = radius

        # Mettre à jour le timer pour les effets visuels
        if hasattr(self.projectile, 'timer'):
            self.projectile.timer = self.timer

        # PulseWaveProjectile: mettre à jour le centre
        if self.proj_type == "PulseWaveProjectile" and hasattr(self.projectile, 'center'):
            self.projectile.center = (x, y)

    @property
    def rect(self):
        return self.projectile.rect

    def draw(self, surface):
        self.projectile.draw(surface)


class MultiplayerGameScreen(Screen):
    """Écran de jeu en mode multijoueur."""

    def __init__(self, screen, scalable_display, client: GameClient):
        super().__init__(screen, scalable_display)
        self.client = client
        self.background = Background()

        self.game_over = False
        self.victory = False
        self.paused = False
        self.player_crashing = False
        self.fade_timer = 0
        self.fade_duration = 240  # 4 secondes à 60 FPS

        # Cache des entités locales (pour le rendu)
        self.players = {}  # player_id -> Player
        self.enemies = {}  # enemy_id -> Enemy/Boss
        self.projectiles = {}  # proj_id -> SyncedProjectile
        self.enemy_projectiles = {}  # proj_id -> SyncedEnemyProjectile
        self.powerups = {}  # (x, y) -> PowerUp
        self.explosions = []
        self.explosion_cache = set()

        # Mapping des types d'ennemis vers leurs classes
        self.enemy_classes = {
            "Enemy": Enemy,
            "ShootingEnemy": ShootingEnemy,
            "Boss": Boss,
            "Boss2": Boss2,
            "Boss3": Boss3,
            "Boss4": Boss4,
            "Boss5": Boss5,
            "Boss6": Boss6,
        }

        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_over or self.victory:
                    self.next_screen = "menu"
                    self.running = False
                else:
                    self.paused = not self.paused

        if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN):
            if self.game_over or self.victory:
                self.next_screen = "menu"
                self.running = False

    def update(self):
        if self.paused:
            return

        if not self.client.connected:
            self.game_over = True
            return

        if self.client.game_over:
            self.game_over = True
            if not self.player_crashing:
                self.player_crashing = True
                self.fade_timer = 0
            if self.player_crashing and self.fade_timer < self.fade_duration:
                self.fade_timer += 1
            return
        if self.client.victory:
            self.victory = True
            return

        # Envoyer les inputs
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        shoot = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
        self.client.send_input(dx, dy, shoot)

        # Synchroniser les entités depuis le serveur
        self._sync_players()
        self._sync_enemies()
        self._sync_projectiles()
        self._sync_powerups()
        self._sync_explosions()

        # Vérifier si tous les joueurs sont morts pour commencer le fondu
        if not self.player_crashing and not self.game_over:
            all_players_dead = all(p.hp <= 0 for p in self.players.values())
            if all_players_dead and len(self.players) > 0:
                self.player_crashing = True
                self.fade_timer = 0
                print("[DEBUG] Tous les joueurs sont morts, début du fondu")

        # Incrémenter le fade_timer si le fondu est actif (même avant le game_over officiel)
        if self.player_crashing and self.fade_timer < self.fade_duration:
            self.fade_timer += 1

        # Mettre à jour les explosions locales
        for exp in self.explosions:
            exp.update()
        self.explosions = [exp for exp in self.explosions if not exp.is_finished()]

        self.background.update()

    def _sync_players(self):
        """Synchronise les joueurs depuis le serveur."""
        server_players = self.client.game_state.get("players", [])

        for p_data in server_players:
            pid = p_data.get("player_id")
            x = p_data.get("x", 0)
            y = p_data.get("y", 0)

            if pid not in self.players:
                self.players[pid] = Player(x, y, player_id=pid, is_local=(pid == self.client.player_id))

            player = self.players[pid]
            player.rect.centerx = x
            player.rect.centery = y
            player.hp = p_data.get("hp", player.hp)
            player.power_type = p_data.get("power_type", "normal")
            player.invulnerable = p_data.get("invulnerable", False)

            # Synchroniser l'état de crash
            is_crashing = p_data.get("is_crashing", False)
            if is_crashing and not player.is_crashing:
                # Démarrer l'animation de crash localement
                player.start_crash()
            player.is_crashing = is_crashing

            if player.is_crashing:
                player.update()
            else:
                # particules du thruster
                player.thruster_timer += 1
                if player.thruster_timer % 2 == 0:
                    base_x = player.rect.centerx
                    base_y = player.rect.bottom - 5
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
                        player.thruster_particles.append(particle)
                for p in player.thruster_particles:
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    p['life'] -= 1
                    p['size'] = max(0, p['size'] - 0.2)
                player.thruster_particles = [p for p in player.thruster_particles if p['life'] > 0]

    def _sync_enemies(self):
        """Synchronise les ennemis depuis le serveur."""
        server_enemies = self.client.game_state.get("enemies", [])
        server_ids = set()

        for e_data in server_enemies:
            eid = e_data.get("enemy_id")
            server_ids.add(eid)
            x = e_data.get("x", 0)
            y = e_data.get("y", 0)
            enemy_type = e_data.get("enemy_type", "Enemy")

            if eid not in self.enemies:
                enemy_class = self.enemy_classes.get(enemy_type, Enemy)
                try:
                    self.enemies[eid] = enemy_class(x, y)
                except Exception:
                    self.enemies[eid] = Enemy(x, y)

            enemy = self.enemies[eid]
            enemy.rect.centerx = x
            enemy.rect.centery = y

            if hasattr(enemy, 'hp'):
                enemy.hp = e_data.get("hp", enemy.hp)
            if hasattr(enemy, 'is_dying'):
                enemy.is_dying = e_data.get("is_dying", False)

            # Synchroniser les animations des boss
            if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                # Déclencher l'animation de dégâts si le serveur l'indique
                damage_anim = e_data.get("damage_animation_active", False)
                if damage_anim and not enemy.damage_animation_active:
                    enemy.damage_animation_active = True
                    enemy.damage_animation_timer = 0

                # Synchroniser l'animation de tir pour Boss 1
                if isinstance(enemy, Boss):
                    shoot_anim = e_data.get("animation_active", False)
                    if shoot_anim and not enemy.animation_active:
                        enemy.animation_active = True
                        enemy.current_animation_frame = 0
                        enemy.animation_timer = 0
                        enemy.image = enemy.shoot_animation_frames[0]

                # Mettre à jour les animations localement (comme en solo)
                self._update_boss_animation(enemy)

            # Données spécifiques Boss3
            if isinstance(enemy, Boss3):
                enemy.laser_active = e_data.get("laser_active", False)
                enemy.laser_warning = e_data.get("laser_warning", False)
                if enemy.laser_active or enemy.laser_warning:
                    enemy.laser_target_x = e_data.get("laser_target_x", x)

            # Données spécifiques Boss4
            if isinstance(enemy, Boss4):
                enemy.charging = e_data.get("charging", False)

            # Mettre à jour les pupilles du Boss1 côté client
            if isinstance(enemy, Boss):
                self._update_boss1_eyes(enemy)

        # Supprimer les ennemis absents
        for eid in list(self.enemies.keys()):
            if eid not in server_ids:
                del self.enemies[eid]

    def _sync_projectiles(self):
        """Synchronise les projectiles depuis le serveur."""
        # Projectiles des joueurs
        server_projs = self.client.game_state.get("projectiles", [])
        server_proj_ids = set()

        for p_data in server_projs:
            pid = p_data.get("proj_id")
            server_proj_ids.add(pid)
            x = p_data.get("x", 0)
            y = p_data.get("y", 0)

            if pid not in self.projectiles:
                self.projectiles[pid] = SyncedProjectile(x, y)

            self.projectiles[pid].sync_position(x, y)

        for pid in list(self.projectiles.keys()):
            if pid not in server_proj_ids:
                del self.projectiles[pid]

        # Projectiles ennemis
        server_enemy_projs = self.client.game_state.get("enemy_projectiles", [])
        server_enemy_proj_ids = set()

        for p_data in server_enemy_projs:
            pid = p_data.get("proj_id")
            server_enemy_proj_ids.add(pid)
            x = p_data.get("x", 0)
            y = p_data.get("y", 0)
            proj_type = p_data.get("proj_type", "EnemyProjectile")
            radius = p_data.get("radius", 5)

            if pid not in self.enemy_projectiles:
                self.enemy_projectiles[pid] = SyncedEnemyProjectile(x, y, proj_type, radius)

            self.enemy_projectiles[pid].sync_position(x, y, radius)

        for pid in list(self.enemy_projectiles.keys()):
            if pid not in server_enemy_proj_ids:
                del self.enemy_projectiles[pid]

    def _sync_powerups(self):
        """Synchronise les powerups depuis le serveur."""
        server_powerups = self.client.game_state.get("powerups", [])
        server_keys = set()

        for pu_data in server_powerups:
            x = pu_data.get("x", 0)
            y = pu_data.get("y", 0)
            power_type = pu_data.get("power_type", "double")
            key = (x, y, power_type)
            server_keys.add(key)

            if key not in self.powerups:
                self.powerups[key] = PowerUp(x, y, power_type)

            powerup = self.powerups[key]
            powerup.rect.centerx = x
            powerup.rect.centery = y

        for key in list(self.powerups.keys()):
            if key not in server_keys:
                del self.powerups[key]

    def _update_boss1_eyes(self, boss):
        """Met à jour les pupilles du Boss1 pour qu'elles suivent les joueurs."""
        import math

        # Récupérer les joueurs vivants triés par player_id
        alive_players = [p for p in sorted(self.players.values(), key=lambda x: x.player_id)
                        if p.hp > 0]

        # Déterminer les cibles pour chaque œil
        left_eye_target = None
        right_eye_target = None

        if len(alive_players) >= 2:
            # Deux joueurs vivants : œil gauche suit joueur 1, œil droit suit joueur 2
            left_eye_target = alive_players[0].rect.center
            right_eye_target = alive_players[1].rect.center
        elif len(alive_players) == 1:
            # Un seul joueur vivant : les deux yeux le suivent
            left_eye_target = alive_players[0].rect.center
            right_eye_target = alive_players[0].rect.center

        # Mise à jour de l'œil gauche
        if left_eye_target:
            px, py = left_eye_target
            eye_left_world_x = boss.rect.left + boss.eye_left_center[0]
            eye_left_world_y = boss.rect.top + boss.eye_left_center[1]
            dx_left = px - eye_left_world_x
            dy_left = py - eye_left_world_y
            dist_left = math.sqrt(dx_left**2 + dy_left**2)

            if dist_left > 0:
                dx_left /= dist_left
                dy_left /= dist_left
                max_offset_x_left = boss.eye_left_radius_x - 3
                max_offset_y_left = boss.eye_left_radius_y - 3
                boss.pupil_left_offset = (dx_left * max_offset_x_left, dy_left * max_offset_y_left)

        # Mise à jour de l'œil droit
        if right_eye_target:
            px, py = right_eye_target
            eye_right_world_x = boss.rect.left + boss.eye_right_center[0]
            eye_right_world_y = boss.rect.top + boss.eye_right_center[1]
            dx_right = px - eye_right_world_x
            dy_right = py - eye_right_world_y
            dist_right = math.sqrt(dx_right**2 + dy_right**2)

            if dist_right > 0:
                dx_right /= dist_right
                dy_right /= dist_right
                max_offset_x_right = boss.eye_right_radius_x - 3
                max_offset_y_right = boss.eye_right_radius_y - 3
                boss.pupil_right_offset = (dx_right * max_offset_x_right, dy_right * max_offset_y_right)

    def _update_boss_animation(self, enemy):
        """Met à jour les animations d'un boss localement (reproduit la logique solo)."""
        # Incrémenter les timers locaux
        enemy.timer = getattr(enemy, 'timer', 0) + 1
        if hasattr(enemy, 'pulse_timer'):
            enemy.pulse_timer += 1

        # === Boss1 ===
        if isinstance(enemy, Boss):
            if enemy.damage_animation_active:
                enemy.damage_animation_timer += 1
                frame = (enemy.damage_animation_timer // enemy.damage_flash_interval) % 2
                if frame == 0:
                    enemy.image = enemy.sprite_damaged_1
                else:
                    enemy.image = enemy.sprite_damaged_2
                if enemy.damage_animation_timer >= enemy.damage_animation_duration:
                    enemy.damage_animation_active = False
                    enemy.damage_animation_timer = 0
                    enemy.image = enemy.sprite_normal
            elif enemy.animation_active:
                # Animation de tir (bouche)
                enemy.animation_timer += 1
                if enemy.animation_timer >= enemy.frames_per_animation_step:
                    enemy.animation_timer = 0
                    enemy.current_animation_frame += 1
                    if enemy.current_animation_frame >= len(enemy.shoot_animation_frames):
                        enemy.animation_active = False
                        enemy.current_animation_frame = 0
                        enemy.image = enemy.sprite_normal
                    else:
                        enemy.image = enemy.shoot_animation_frames[enemy.current_animation_frame]
            elif enemy.is_dying:
                frame = (enemy.timer // 5) % 2
                if frame == 0:
                    enemy.image = enemy.sprite_damaged_1
                else:
                    enemy.image = enemy.sprite_damaged_2
            elif not enemy.damage_animation_active:
                enemy.image = enemy.sprite_normal

        # === Boss2 ===
        elif isinstance(enemy, Boss2):
            if enemy.damage_animation_active:
                enemy.damage_animation_timer += 1
                if (enemy.damage_animation_timer // enemy.damage_flash_interval) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()
                if enemy.damage_animation_timer >= enemy.damage_animation_duration:
                    enemy.damage_animation_active = False
                    enemy.damage_animation_timer = 0
                    enemy.image = enemy._create_boss_sprite()
            elif enemy.is_dying:
                if (enemy.timer // 3) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()

        # === Boss3 ===
        elif isinstance(enemy, Boss3):
            enemy.core_rotation = getattr(enemy, 'core_rotation', 0) + 2
            if enemy.damage_animation_active:
                enemy.damage_animation_timer += 1
                if (enemy.damage_animation_timer // enemy.damage_flash_interval) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()
                if enemy.damage_animation_timer >= enemy.damage_animation_duration:
                    enemy.damage_animation_active = False
                    enemy.damage_animation_timer = 0
                    enemy.image = enemy._create_boss_sprite()
            elif enemy.is_dying:
                if (enemy.timer // 2) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()

        # === Boss4 ===
        elif isinstance(enemy, Boss4):
            enemy.ring_rotation = getattr(enemy, 'ring_rotation', 0) + 1
            if enemy.damage_animation_active:
                enemy.damage_animation_timer += 1
                if (enemy.damage_animation_timer // enemy.damage_flash_interval) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()
                if enemy.damage_animation_timer >= enemy.damage_animation_duration:
                    enemy.damage_animation_active = False
                    enemy.damage_animation_timer = 0
                    enemy.image = enemy._create_boss_sprite()
            elif enemy.is_dying:
                if (enemy.timer // 2) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_boss_sprite()

        # === Boss5 ===
        elif isinstance(enemy, Boss5):
            enemy.eye_glow = abs(math.sin(enemy.pulse_timer * 0.05)) * 50
            # Mode rage
            if enemy.hp <= enemy.max_hp * 0.3 and not enemy.rage_mode:
                enemy.rage_mode = True
            if enemy.rage_mode:
                enemy.rage_pulse = getattr(enemy, 'rage_pulse', 0) + 3

            if enemy.damage_animation_active:
                enemy.damage_animation_timer += 1
                if (enemy.damage_animation_timer // enemy.damage_flash_interval) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_rage_sprite() if enemy.rage_mode else enemy._create_boss_sprite()
                if enemy.damage_animation_timer >= enemy.damage_animation_duration:
                    enemy.damage_animation_active = False
                    enemy.damage_animation_timer = 0
                    enemy.image = enemy._create_rage_sprite() if enemy.rage_mode else enemy._create_boss_sprite()
            elif enemy.is_dying:
                if (enemy.timer // 2) % 2 == 0:
                    enemy.image = enemy._create_damaged_sprite()
                else:
                    enemy.image = enemy._create_rage_sprite() if enemy.rage_mode else enemy._create_boss_sprite()
            else:
                enemy.image = enemy._create_rage_sprite() if enemy.rage_mode else enemy._create_boss_sprite()

        # === Boss6 ===
        elif isinstance(enemy, Boss6):
            # Mode fury
            if enemy.hp <= enemy.max_hp * 0.25 and not enemy.fury_mode:
                enemy.fury_mode = True
            # Rotation
            enemy.rotation_angle = getattr(enemy, 'rotation_angle', 0) + (4 if enemy.fury_mode else 2)
            enemy.distortion_angle = getattr(enemy, 'distortion_angle', 0) + 0.05

            if enemy.is_dying:
                # Animation de mort avec rétrécissement
                enemy.death_timer = getattr(enemy, 'death_timer', 0) + 1
                if enemy.death_timer < 120:
                    shrink = 1 - (enemy.death_timer / 120) * 0.5
                    enemy.image = pygame.transform.rotozoom(
                        enemy.base_image,
                        enemy.rotation_angle + enemy.death_timer * 5,
                        shrink
                    )
                    enemy.rect = enemy.image.get_rect(center=enemy.rect.center)
            else:
                # Rotation normale
                enemy.image = pygame.transform.rotate(enemy.base_image, enemy.rotation_angle)
                enemy.rect = enemy.image.get_rect(center=enemy.rect.center)

    def _sync_explosions(self):
        """Synchronise les explosions depuis le serveur."""
        server_explosions = self.client.game_state.get("explosions", [])
        current_time = pygame.time.get_ticks()

        for exp_data in server_explosions:
            x = exp_data.get("x", 0)
            y = exp_data.get("y", 0)
            start_time = exp_data.get("start_time", current_time)
            duration = exp_data.get("duration", 300)

            key = (x, y, start_time)
            if key not in self.explosion_cache:
                self.explosion_cache.add(key)
                self.explosions.append(Explosion(x, y, duration=duration))

        self.explosion_cache = {k for k in self.explosion_cache if current_time - k[2] < 2000}

    def draw(self):
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        # Dessiner les powerups
        for powerup in self.powerups.values():
            powerup.draw(self.screen)

        # Dessiner les ennemis
        for enemy in self.enemies.values():
            enemy.draw(self.screen)
            if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                self._draw_boss_health_bar(enemy)

        # Dessiner les projectiles joueurs
        for proj in self.projectiles.values():
            proj.draw(self.screen)

        # Dessiner les projectiles ennemis
        for proj in self.enemy_projectiles.values():
            proj.draw(self.screen)

        # Dessiner les joueurs (même ceux en crash avec HP=0)
        for player in self.players.values():
            if player.hp > 0 or player.is_crashing:
                player.draw(self.screen)

        # Dessiner les explosions
        for exp in self.explosions:
            exp.draw(self.screen)

        # UI
        self._draw_ui()

        # Fondu au noir progressif pendant le crash (4 secondes) et reste noir après
        if self.fade_timer > 0:
            progress = min(1.0, self.fade_timer / self.fade_duration)
            fade_alpha = int(255 * progress)
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            self.screen.blit(fade_surface, (0, 0))

        # Écrans de fin (afficher GAME OVER même pendant le crash)
        if self.player_crashing or self.game_over:
            print(f"[DEBUG DRAW] Affichage game over - player_crashing={self.player_crashing}, game_over={self.game_over}, fade_timer={self.fade_timer}")
            self._draw_game_over()
        elif self.victory:
            self._draw_victory()
        elif self.paused:
            self._draw_pause()

    def _draw_boss_health_bar(self, boss):
        """Dessine la barre de vie d'un boss."""
        max_hp = {
            Boss: 20, Boss2: 30, Boss3: 40,
            Boss4: 50, Boss5: 60, Boss6: 75
        }.get(type(boss), 20)

        bar_width = 80
        bar_height = 8
        bar_x = boss.rect.centerx - bar_width // 2
        bar_y = boss.rect.top - 15

        hp_ratio = max(0, boss.hp / max_hp)
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (255, 50, 50), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_ui(self):
        """Dessine l'interface utilisateur."""
        timer = self.client.game_state.get("timer", 0)

        timer_text = self.font.render(f"Timer: {timer}", True, WHITE)
        self.screen.blit(timer_text, (10, 10))

        y_offset = 50
        for pid, player in self.players.items():
            is_local = (pid == self.client.player_id)
            label = "Vous" if is_local else "Allié"
            hp_color = (100, 255, 100) if player.hp > 2 else (255, 255, 100) if player.hp > 1 else (255, 100, 100)
            if not is_local:
                hp_color = (100, 200, 255)

            hp_text = self.font.render(f"{label}: {player.hp} HP", True, hp_color)
            self.screen.blit(hp_text, (10, y_offset))
            y_offset += 35

            if is_local and player.power_type != "normal":
                power_text = self.small_font.render(f"Power: {player.power_type}", True, CYAN)
                self.screen.blit(power_text, (10, y_offset))
                y_offset += 25

        status_color = (100, 255, 100) if self.client.connected else (255, 100, 100)
        status_text = "En ligne" if self.client.connected else "Déconnecté"
        status = self.small_font.render(status_text, True, status_color)
        self.screen.blit(status, (SCREEN_WIDTH - 100, 10))

        controls = self.small_font.render("ZQSD + Espace", True, (100, 100, 130))
        self.screen.blit(controls, (SCREEN_WIDTH - 130, SCREEN_HEIGHT - 30))

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        game_over_text = big_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        hint_text = self.font.render("Appuyez sur une touche pour revenir au menu", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(hint_text, hint_rect)

    def _draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        victory_text = big_font.render("VICTOIRE !", True, (50, 255, 50))
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)

        coop_text = self.font.render("Félicitations aux deux joueurs !", True, (100, 255, 200))
        coop_rect = coop_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(coop_text, coop_rect)

        hint_text = self.small_font.render("Appuyez sur une touche pour revenir au menu", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(hint_text, hint_rect)

    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 56)
        pause_text = big_font.render("PAUSE", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(pause_text, text_rect)

        hint_text = self.small_font.render("Appuyez sur Échap pour reprendre", True, (180, 180, 180))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(hint_text, hint_rect)
