import pygame
import math
import random

from config import RED, CYAN, ORANGE, SCREEN_WIDTH, SCREEN_HEIGHT
from .projectiles import EnemyProjectile


class Enemy:
    """Classe de base pour tous les ennemis."""
    def __init__(self, x, y, speed=3, movement_pattern=None, color=RED):
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hp = 1
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


class BasicEnemy(Enemy):
    """Ennemi de base rouge - utilisé pour les spawns simples."""
    def __init__(self, x, y, speed=3, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=RED)


class FormationVEnemy(Enemy):
    """Ennemi de formation en V - cyan."""
    def __init__(self, x, y, speed=2.5, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=CYAN)


class FormationLineEnemy(Enemy):
    """Ennemi de formation en ligne horizontale - orange."""
    def __init__(self, x, y, speed=2, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=ORANGE)


class SineWaveEnemy(Enemy):
    """Ennemi avec mouvement sinusoïdal - rose."""
    def __init__(self, x, y, speed=2.5, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=(255, 100, 200))


class ZigZagEnemy(Enemy):
    """Ennemi avec mouvement en zigzag - vert clair."""
    def __init__(self, x, y, speed=3, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=(100, 255, 100))


class SwoopEnemy(Enemy):
    """Ennemi qui fait un piqué depuis les côtés - jaune/or."""
    def __init__(self, x, y, speed=2, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=(255, 200, 0))


class HorizontalEnemy(Enemy):
    """Ennemi d'escadrille horizontale - bleu clair."""
    def __init__(self, x, y, speed=5, movement_pattern=None):
        super().__init__(x, y, speed, movement_pattern, color=(150, 150, 255))


class ShootingEnemy(Enemy):
    def __init__(self, x, y, speed=3, shoot_delay_frames=60):
        super().__init__(x, y, speed)
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.shoot_delay_frames = shoot_delay_frames
        self.last_shot_frame = 0

    def _create_sprite(self):
        """Crée le sprite du ShootingEnemy - un drone ennemi agressif"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Couleurs
        body_color = (180, 30, 180)  # Magenta foncé
        body_highlight = (220, 80, 220)  # Magenta clair
        eye_color = (255, 50, 50)  # Rouge vif pour l'oeil/canon
        wing_color = (120, 20, 120)  # Violet foncé pour les ailes
        outline_color = (80, 10, 80)  # Contour sombre

        center_x, center_y = size // 2, size // 2

        # Corps principal - hexagone aplati (forme de drone)
        body_points = [
            (center_x, center_y - 12),      # Haut
            (center_x + 10, center_y - 6),  # Haut droite
            (center_x + 10, center_y + 6),  # Bas droite
            (center_x, center_y + 12),      # Bas
            (center_x - 10, center_y + 6),  # Bas gauche
            (center_x - 10, center_y - 6),  # Haut gauche
        ]
        pygame.draw.polygon(surface, body_color, body_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Ailes latérales (triangles pointant vers l'extérieur)
        # Aile gauche
        left_wing = [
            (center_x - 10, center_y - 4),
            (center_x - 18, center_y),
            (center_x - 10, center_y + 4),
        ]
        pygame.draw.polygon(surface, wing_color, left_wing)
        pygame.draw.polygon(surface, outline_color, left_wing, 1)

        # Aile droite
        right_wing = [
            (center_x + 10, center_y - 4),
            (center_x + 18, center_y),
            (center_x + 10, center_y + 4),
        ]
        pygame.draw.polygon(surface, wing_color, right_wing)
        pygame.draw.polygon(surface, outline_color, right_wing, 1)

        # Highlight sur le corps (reflet)
        highlight_points = [
            (center_x, center_y - 10),
            (center_x + 6, center_y - 5),
            (center_x + 6, center_y),
            (center_x, center_y + 2),
            (center_x - 6, center_y),
            (center_x - 6, center_y - 5),
        ]
        pygame.draw.polygon(surface, body_highlight, highlight_points)

        # Oeil central / Canon - cercle rouge menaçant
        pygame.draw.circle(surface, eye_color, (center_x, center_y + 2), 5)
        pygame.draw.circle(surface, (255, 150, 150), (center_x - 1, center_y + 1), 2)  # Reflet

        # Canon/Nez pointant vers le bas (direction de tir)
        cannon_points = [
            (center_x - 3, center_y + 12),
            (center_x, center_y + 18),
            (center_x + 3, center_y + 12),
        ]
        pygame.draw.polygon(surface, eye_color, cannon_points)

        return surface

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


class TankEnemy(Enemy):
    """Ennemi blindé - lent mais résistant avec un bouclier frontal"""
    def __init__(self, x, y, speed=1.5):
        super().__init__(x, y, speed)
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 5

    def _create_sprite(self):
        """Crée le sprite du TankEnemy - un vaisseau lourd blindé"""
        size = 50
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Couleurs
        armor_color = (80, 80, 100)  # Gris métallique
        armor_highlight = (120, 120, 140)
        core_color = (200, 50, 50)  # Rouge pour le cœur
        shield_color = (60, 60, 80)
        outline_color = (40, 40, 50)

        center_x, center_y = size // 2, size // 2

        # Corps principal - forme trapézoïdale massive
        body_points = [
            (center_x - 8, center_y - 20),   # Haut gauche
            (center_x + 8, center_y - 20),   # Haut droite
            (center_x + 18, center_y + 15),  # Bas droite
            (center_x - 18, center_y + 15),  # Bas gauche
        ]
        pygame.draw.polygon(surface, armor_color, body_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Bouclier frontal (en haut)
        shield_points = [
            (center_x - 15, center_y - 18),
            (center_x + 15, center_y - 18),
            (center_x + 12, center_y - 25),
            (center_x - 12, center_y - 25),
        ]
        pygame.draw.polygon(surface, shield_color, shield_points)
        pygame.draw.polygon(surface, outline_color, shield_points, 1)

        # Plaques de blindage latérales
        left_plate = [
            (center_x - 18, center_y - 10),
            (center_x - 22, center_y),
            (center_x - 18, center_y + 10),
        ]
        pygame.draw.polygon(surface, armor_highlight, left_plate)

        right_plate = [
            (center_x + 18, center_y - 10),
            (center_x + 22, center_y),
            (center_x + 18, center_y + 10),
        ]
        pygame.draw.polygon(surface, armor_highlight, right_plate)

        # Cœur/réacteur central (point faible visuel)
        pygame.draw.circle(surface, core_color, (center_x, center_y + 5), 6)
        pygame.draw.circle(surface, (255, 100, 100), (center_x - 2, center_y + 3), 2)

        # Détails de rivets
        rivet_positions = [(center_x - 10, center_y - 5), (center_x + 10, center_y - 5),
                          (center_x - 10, center_y + 8), (center_x + 10, center_y + 8)]
        for pos in rivet_positions:
            pygame.draw.circle(surface, outline_color, pos, 2)

        return surface


class DashEnemy(Enemy):
    """Ennemi rapide qui charge vers le joueur après une pause"""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed)
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        self.dash_speed = 12
        self.is_dashing = False
        self.dash_direction = (0, 1)
        self.pause_duration = 60
        self.warning_duration = 30

    def _create_sprite(self):
        """Crée le sprite du DashEnemy - un chasseur agile"""
        size = 35
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Couleurs
        body_color = (255, 120, 0)  # Orange vif
        engine_color = (255, 200, 50)  # Jaune pour les réacteurs
        outline_color = (150, 60, 0)

        center_x, center_y = size // 2, size // 2

        # Corps aérodynamique - forme de flèche pointue
        body_points = [
            (center_x, center_y - 15),       # Pointe avant
            (center_x + 12, center_y + 10),  # Aile droite
            (center_x + 5, center_y + 8),    # Retrait droite
            (center_x, center_y + 12),       # Queue
            (center_x - 5, center_y + 8),    # Retrait gauche
            (center_x - 12, center_y + 10),  # Aile gauche
        ]
        pygame.draw.polygon(surface, body_color, body_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Highlight central
        highlight_points = [
            (center_x, center_y - 12),
            (center_x + 5, center_y + 5),
            (center_x, center_y + 8),
            (center_x - 5, center_y + 5),
        ]
        pygame.draw.polygon(surface, (255, 180, 100), highlight_points)

        # Réacteurs arrière
        pygame.draw.circle(surface, engine_color, (center_x - 4, center_y + 10), 3)
        pygame.draw.circle(surface, engine_color, (center_x + 4, center_y + 10), 3)

        # Cockpit/œil
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y - 5), 4)
        pygame.draw.circle(surface, (255, 50, 50), (center_x, center_y - 5), 2)

        return surface

    def update_with_player(self, player_position):
        """Mise à jour avec la position du joueur pour le dash"""
        self.timer += 1

        if self.timer < self.pause_duration:
            # Phase d'approche lente
            self.rect.y += self.speed
        elif self.timer < self.pause_duration + self.warning_duration:
            # Phase d'avertissement - l'ennemi "vise"
            if not self.is_dashing:
                px, py = player_position
                dx = px - self.rect.centerx
                dy = py - self.rect.centery
                dist = (dx**2 + dy**2) ** 0.5
                if dist > 0:
                    self.dash_direction = (dx / dist, dy / dist)
        else:
            # Phase de dash
            self.is_dashing = True
            self.rect.x += self.dash_direction[0] * self.dash_speed
            self.rect.y += self.dash_direction[1] * self.dash_speed


class SplitterEnemy(Enemy):
    """Ennemi qui se divise en mini-ennemis quand il est détruit"""
    def __init__(self, x, y, speed=2, is_mini=False):
        super().__init__(x, y, speed)
        self.is_mini = is_mini
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 1 if is_mini else 3

    def _create_sprite(self):
        """Crée le sprite du SplitterEnemy"""
        size = 25 if self.is_mini else 45
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Couleurs
        if self.is_mini:
            body_color = (100, 200, 100)  # Vert clair pour les minis
            core_color = (150, 255, 150)
        else:
            body_color = (50, 150, 50)  # Vert foncé pour le principal
            core_color = (100, 200, 100)

        outline_color = (30, 100, 30)
        center_x, center_y = size // 2, size // 2

        # Corps cellulaire - forme organique
        if self.is_mini:
            pygame.draw.circle(surface, body_color, (center_x, center_y), size // 2 - 2)
            pygame.draw.circle(surface, core_color, (center_x, center_y), size // 4)
            pygame.draw.circle(surface, outline_color, (center_x, center_y), size // 2 - 2, 2)
        else:
            # Corps principal avec "bourgeonnements"
            pygame.draw.circle(surface, body_color, (center_x, center_y), size // 2 - 5)

            # Bourgeons (futurs minis)
            bud_positions = [
                (center_x - 12, center_y - 8),
                (center_x + 12, center_y - 8),
                (center_x, center_y + 12),
            ]
            for pos in bud_positions:
                pygame.draw.circle(surface, core_color, pos, 6)
                pygame.draw.circle(surface, outline_color, pos, 6, 1)

            # Noyau central
            pygame.draw.circle(surface, core_color, (center_x, center_y), 8)
            pygame.draw.circle(surface, (200, 255, 200), (center_x - 2, center_y - 2), 3)

            # Contour organique
            pygame.draw.circle(surface, outline_color, (center_x, center_y), size // 2 - 5, 2)

        return surface

    def split(self):
        """Retourne une liste de mini-ennemis lors de la destruction"""
        if self.is_mini:
            return []

        mini_enemies = []
        offsets = [(-20, -15), (20, -15), (0, 20)]
        for offset_x, offset_y in offsets:
            mini = SplitterEnemy(
                self.rect.centerx + offset_x,
                self.rect.centery + offset_y,
                speed=3,
                is_mini=True
            )
            mini_enemies.append(mini)
        return mini_enemies


class SniperEnemy(Enemy):
    """Ennemi sniper - descend, s'immobilise, vise avec un laser rouge, tire un tir ultra-rapide."""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed, color=(100, 0, 200))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        # Phases : 0=descente, 1=visée, 2=recharge
        self.phase = 0
        self.phase_timer = 0
        self.last_player_pos = (x, y + 200)

    def _create_sprite(self):
        size = 38
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps allongé style sniper
        body = [(cx, cy - 16), (cx + 7, cy - 6), (cx + 5, cy + 12), (cx - 5, cy + 12), (cx - 7, cy - 6)]
        pygame.draw.polygon(surface, (100, 0, 200), body)
        pygame.draw.polygon(surface, (50, 0, 100), body, 2)

        # Ailes fines
        left_wing = [(cx - 7, cy - 2), (cx - 18, cy + 8), (cx - 5, cy + 10)]
        right_wing = [(cx + 7, cy - 2), (cx + 18, cy + 8), (cx + 5, cy + 10)]
        pygame.draw.polygon(surface, (70, 0, 150), left_wing)
        pygame.draw.polygon(surface, (70, 0, 150), right_wing)
        pygame.draw.polygon(surface, (50, 0, 100), left_wing, 1)
        pygame.draw.polygon(surface, (50, 0, 100), right_wing, 1)

        # Canon long pointant vers le bas
        pygame.draw.rect(surface, (160, 0, 255), (cx - 2, cy + 10, 4, 14))
        pygame.draw.rect(surface, (200, 100, 255), (cx - 1, cy + 10, 2, 12))

        # Viseur/œil
        pygame.draw.circle(surface, (255, 50, 50), (cx, cy - 2), 4)
        pygame.draw.circle(surface, (255, 200, 200), (cx - 1, cy - 3), 1)

        return surface

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        self.phase_timer += 1
        self.last_player_pos = player_position

        if self.phase == 0:
            # Descente vers position de tir
            self.rect.y += self.speed
            if self.phase_timer >= 90:
                self.phase = 1
                self.phase_timer = 0
        elif self.phase == 1:
            # Visée - immobile, laser actif
            if self.phase_timer >= 60:
                proj = self._fire(player_position)
                enemy_projectiles.append(proj)
                self.phase = 2
                self.phase_timer = 0
        elif self.phase == 2:
            # Recharge, descente lente
            self.rect.y += self.speed * 0.4
            if self.phase_timer >= 120:
                self.phase = 1
                self.phase_timer = 0

    def _fire(self, player_position):
        ex, ey = self.rect.center
        px, py = player_position
        dx = px - ex
        dy = py - ey
        dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
        return EnemyProjectile(ex, ey, dx / dist, dy / dist, speed=14)

    def draw(self, surface):
        # Laser de visée rouge pendant la phase 1
        if self.phase == 1:
            intensity = min(255, self.phase_timer * 4)
            laser_color = (255, max(0, 80 - intensity), max(0, 80 - intensity))
            ex, ey = self.rect.center
            px, py = self.last_player_pos
            pygame.draw.line(surface, laser_color, (ex, ey + 14), (px, py), 1)
            pygame.draw.circle(surface, (255, 100, 100), (ex, ey + 14), 3)
        surface.blit(self.image, self.rect)


class MineEnemy(Enemy):
    """Ennemi mine - descend très lentement et explose en 8 projectiles quand détruit."""
    def __init__(self, x, y, speed=1.2):
        super().__init__(x, y, speed, color=(160, 60, 0))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2

    def _create_sprite(self):
        size = 38
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps sphérique principal
        pygame.draw.circle(surface, (130, 50, 0), (cx, cy), 12)
        pygame.draw.circle(surface, (180, 80, 0), (cx, cy), 9)
        pygame.draw.circle(surface, (220, 130, 0), (cx - 2, cy - 2), 4)
        pygame.draw.circle(surface, (80, 30, 0), (cx, cy), 12, 2)

        # 8 pointes en étoile
        for i in range(8):
            angle = i * math.pi / 4
            tip_x = cx + int(math.cos(angle) * 17)
            tip_y = cy + int(math.sin(angle) * 17)
            b1x = cx + int(math.cos(angle + 0.4) * 11)
            b1y = cy + int(math.sin(angle + 0.4) * 11)
            b2x = cx + int(math.cos(angle - 0.4) * 11)
            b2y = cy + int(math.sin(angle - 0.4) * 11)
            pygame.draw.polygon(surface, (150, 55, 0), [(tip_x, tip_y), (b1x, b1y), (b2x, b2y)])
            pygame.draw.polygon(surface, (80, 30, 0), [(tip_x, tip_y), (b1x, b1y), (b2x, b2y)], 1)

        return surface

    def explode(self):
        """Retourne 8 projectiles en étoile lors de l'explosion."""
        projectiles = []
        ex, ey = self.rect.center
        for i in range(8):
            angle = i * math.pi / 4
            dx = math.cos(angle)
            dy = math.sin(angle)
            projectiles.append(EnemyProjectile(ex, ey, dx, dy, speed=5))
        return projectiles


class ShieldEnemy(Enemy):
    """Ennemi avec bouclier frontal - les tirs qui frappent le bouclier sont bloqués."""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed, color=(0, 150, 200))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 3
        self._shield_w = 36
        self._shield_h = 10

    def _create_sprite(self):
        size = 44
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps principal
        body = [(cx, cy - 14), (cx + 10, cy - 4), (cx + 10, cy + 8), (cx - 10, cy + 8), (cx - 10, cy - 4)]
        pygame.draw.polygon(surface, (0, 100, 180), body)
        pygame.draw.polygon(surface, (0, 50, 120), body, 2)

        # Détail central
        pygame.draw.circle(surface, (0, 160, 220), (cx, cy - 2), 5)
        pygame.draw.circle(surface, (100, 220, 255), (cx - 1, cy - 3), 2)

        # Bouclier frontal (en bas)
        shield_pts = [(cx - 18, cy + 8), (cx + 18, cy + 8), (cx + 15, cy + 20), (cx - 15, cy + 20)]
        pygame.draw.polygon(surface, (0, 200, 255), shield_pts)
        pygame.draw.polygon(surface, (0, 120, 200), shield_pts, 2)
        # Reflet sur le bouclier
        pygame.draw.line(surface, (180, 240, 255), (cx - 12, cy + 11), (cx + 12, cy + 11), 2)

        return surface

    def get_shield_rect(self):
        """Retourne le rect du bouclier frontal."""
        return pygame.Rect(
            self.rect.centerx - self._shield_w // 2,
            self.rect.bottom - 14,
            self._shield_w,
            self._shield_h
        )

    def is_blocked_by_shield(self, projectile_rect):
        """Vérifie si un projectile heurte le bouclier."""
        return self.get_shield_rect().colliderect(projectile_rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Lueur du bouclier
        sr = self.get_shield_rect()
        glow = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (0, 200, 255, 70), (0, 0, sr.width, sr.height))
        surface.blit(glow, sr)


class GhostEnemy(Enemy):
    """Ennemi fantôme - alterne visible/invincible et tire vers le joueur depuis l'ombre."""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed, color=(200, 220, 255))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        self.ghost_cycle = 120       # Frames par cycle
        self.ghost_visible_time = 70  # Frames visibles dans le cycle
        self.last_player_pos = (x, y + 200)
        self.shot_cooldown = 0
        self.shoot_interval = 80

    def _create_sprite(self):
        size = 38
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps fantomatique
        body_pts = [
            (cx, cy - 15), (cx + 12, cy - 4), (cx + 12, cy + 8),
            (cx + 8, cy + 5), (cx + 4, cy + 15), (cx, cy + 11),
            (cx - 4, cy + 15), (cx - 8, cy + 5), (cx - 12, cy + 8), (cx - 12, cy - 4)
        ]
        pygame.draw.polygon(surface, (180, 200, 255), body_pts)
        pygame.draw.polygon(surface, (100, 130, 220), body_pts, 2)

        # Yeux
        pygame.draw.circle(surface, (40, 40, 200), (cx - 4, cy - 2), 4)
        pygame.draw.circle(surface, (40, 40, 200), (cx + 4, cy - 2), 4)
        pygame.draw.circle(surface, (200, 200, 255), (cx - 3, cy - 3), 2)
        pygame.draw.circle(surface, (200, 200, 255), (cx + 5, cy - 3), 2)

        # Halo
        halo = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(halo, (150, 180, 255, 35), (cx, cy), 16)
        surface.blit(halo, (0, 0))

        return surface

    def is_invisible(self):
        """Retourne True quand le fantôme est en phase invisible/invincible."""
        return (self.timer % self.ghost_cycle) >= self.ghost_visible_time

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        self.last_player_pos = player_position
        self.rect.y += self.speed
        # Oscillation horizontale lente
        self.rect.x = self.start_x + int(math.sin(self.timer * 0.03) * 30)

        if not self.is_invisible():
            self.shot_cooldown += 1
            if self.shot_cooldown >= self.shoot_interval:
                self.shot_cooldown = 0
                ex, ey = self.rect.center
                px, py = player_position
                dx = px - ex
                dy = py - ey
                dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
                enemy_projectiles.append(EnemyProjectile(ex, ey, dx / dist, dy / dist, speed=5))

    def draw(self, surface):
        cycle_pos = self.timer % self.ghost_cycle
        if cycle_pos < self.ghost_visible_time:
            alpha = 255
        else:
            fade_len = self.ghost_cycle - self.ghost_visible_time
            fade_pos = cycle_pos - self.ghost_visible_time
            half = fade_len // 2
            if fade_pos < half:
                alpha = int(255 * (1 - fade_pos / half))
            else:
                alpha = int(255 * ((fade_pos - half) / half))
            alpha = max(30, alpha)

        ghost_surf = self.image.copy()
        ghost_surf.set_alpha(alpha)
        surface.blit(ghost_surf, self.rect)


class BomberEnemy(Enemy):
    """Ennemi kamikaze - fonce vers le joueur et explose en 6 projectiles à sa mort."""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed, color=(200, 40, 0))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        self.dash_speed = 15
        self.dash_direction = (0, 1)
        self.approach_duration = 50
        self.warning_duration = 25
        self.is_dashing = False

    def _create_sprite(self):
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps trapu
        body = [
            (cx, cy - 17), (cx + 13, cy - 5), (cx + 14, cy + 8),
            (cx, cy + 15), (cx - 14, cy + 8), (cx - 13, cy - 5)
        ]
        pygame.draw.polygon(surface, (180, 35, 0), body)
        pygame.draw.polygon(surface, (100, 20, 0), body, 2)

        # Bandes danger jaune
        pygame.draw.polygon(surface, (255, 200, 0), [
            (cx - 4, cy - 14), (cx + 4, cy - 14), (cx + 4, cy - 7), (cx - 4, cy - 7)
        ])
        pygame.draw.polygon(surface, (255, 200, 0), [
            (cx - 4, cy - 2), (cx + 4, cy - 2), (cx + 4, cy + 5), (cx - 4, cy + 5)
        ])

        # Tête de mort simplifiée
        pygame.draw.circle(surface, (240, 240, 240), (cx, cy - 5), 6)
        pygame.draw.circle(surface, (180, 35, 0), (cx - 2, cy - 7), 2)
        pygame.draw.circle(surface, (180, 35, 0), (cx + 2, cy - 7), 2)
        pygame.draw.line(surface, (180, 35, 0), (cx - 3, cy - 2), (cx + 3, cy - 2), 2)

        # Réacteur arrière
        pygame.draw.circle(surface, (255, 200, 0), (cx, cy + 13), 5)
        pygame.draw.circle(surface, (255, 255, 150), (cx, cy + 13), 2)

        return surface

    def update_with_player(self, player_position):
        self.timer += 1

        if self.timer < self.approach_duration:
            self.rect.y += self.speed
        elif self.timer < self.approach_duration + self.warning_duration:
            # Calcul de la direction vers le joueur
            if not self.is_dashing:
                px, py = player_position
                dx = px - self.rect.centerx
                dy = py - self.rect.centery
                dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
                self.dash_direction = (dx / dist, dy / dist)
        else:
            self.is_dashing = True
            self.rect.x += int(self.dash_direction[0] * self.dash_speed)
            self.rect.y += int(self.dash_direction[1] * self.dash_speed)

    def explode(self):
        """Retourne 6 projectiles en étoile lors de l'explosion."""
        projectiles = []
        ex, ey = self.rect.center
        for i in range(6):
            angle = i * math.pi / 3
            dx = math.cos(angle)
            dy = math.sin(angle)
            projectiles.append(EnemyProjectile(ex, ey, dx, dy, speed=6))
        return projectiles

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.is_dashing:
            # Flamme dans la direction opposée au dash
            fx = self.rect.centerx + int(-self.dash_direction[0] * 16)
            fy = self.rect.centery + int(-self.dash_direction[1] * 16)
            flame_r = 6 + (self.timer % 4)
            pygame.draw.circle(surface, (255, 140, 0), (fx, fy), flame_r)
            pygame.draw.circle(surface, (255, 255, 100), (fx, fy), flame_r // 2)
        elif self.timer >= self.approach_duration and not self.is_dashing:
            # Clignotement rouge d'avertissement
            if (self.timer // 5) % 2 == 0:
                warn = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(warn, (255, 0, 0, 110), (0, 0, self.rect.width + 8, self.rect.height + 8), 3)
                surface.blit(warn, (self.rect.x - 4, self.rect.y - 4))


class TeleporterEnemy(Enemy):
    """Ennemi téléporteur - descend, puis se téléporte brusquement en tirant une rafale en éventail."""
    def __init__(self, x, y, speed=1.5):
        super().__init__(x, y, speed, color=(220, 0, 180))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        self.teleport_interval = 80
        self.teleport_flash = 0  # Timer du flash post-téléportation

    def _create_sprite(self):
        size = 36
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps style portail tourbillonnant
        pygame.draw.circle(surface, (170, 0, 135), (cx, cy), 14)
        pygame.draw.circle(surface, (235, 55, 195), (cx, cy), 10)
        # Anneaux de distorsion
        for r in [6, 9, 13]:
            pygame.draw.circle(surface, (255, 120, 240), (cx, cy), r, 1)
        # Centre lumineux
        pygame.draw.circle(surface, (255, 200, 255), (cx, cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)

        return surface

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        if self.teleport_flash > 0:
            self.teleport_flash -= 1
        self.rect.y += self.speed

        if self.timer > 0 and self.timer % self.teleport_interval == 0:
            new_x = random.randint(80, SCREEN_WIDTH - 80)
            new_y = random.randint(60, SCREEN_HEIGHT // 2)
            self.rect.center = (new_x, new_y)
            self.start_x = new_x
            self.teleport_flash = 15
            # Rafale de 3 projectiles ciblée en éventail
            px, py = player_position
            base_angle = math.atan2(py - new_y, px - new_x)
            for spread in (-20, 0, 20):
                angle = base_angle + math.radians(spread)
                enemy_projectiles.append(
                    EnemyProjectile(new_x, new_y, math.cos(angle), math.sin(angle), speed=6)
                )

    def draw(self, surface):
        if self.teleport_flash > 0:
            glow_r = 26
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            alpha = int(185 * self.teleport_flash / 15)
            pygame.draw.circle(glow_surf, (255, 150, 255, alpha), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (self.rect.centerx - glow_r, self.rect.centery - glow_r))

        # Clignotement 20 frames avant la téléportation
        frames_left = self.teleport_interval - (self.timer % self.teleport_interval)
        if frames_left <= 20 and (self.timer // 3) % 2 == 1:
            return  # Frame sautée (effet clignotement)
        surface.blit(self.image, self.rect)


class PulseEnemy(Enemy):
    """Ennemi pulseur - descend lentement et libère des anneaux de 8 projectiles."""
    def __init__(self, x, y, speed=1.2):
        super().__init__(x, y, speed, color=(0, 200, 255))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 3
        self.pulse_interval = 90

    def _create_sprite(self):
        size = 44
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Hexagone électrique
        hex_pts = [
            (cx + int(math.cos(i * math.pi / 3 - math.pi / 6) * 14),
             cy + int(math.sin(i * math.pi / 3 - math.pi / 6) * 14))
            for i in range(6)
        ]
        pygame.draw.polygon(surface, (0, 140, 210), hex_pts)
        pygame.draw.polygon(surface, (0, 70, 150), hex_pts, 2)

        # Anneaux intérieurs
        pygame.draw.circle(surface, (0, 210, 255), (cx, cy), 9)
        pygame.draw.circle(surface, (0, 90, 180), (cx, cy), 9, 2)

        # Noyau
        pygame.draw.circle(surface, (140, 240, 255), (cx, cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)

        return surface

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed

        if self.timer % self.pulse_interval == 0:
            ex, ey = self.rect.center
            for i in range(8):
                angle = i * math.pi / 4
                enemy_projectiles.append(
                    EnemyProjectile(ex, ey, math.cos(angle), math.sin(angle), speed=4)
                )

    def draw(self, surface):
        # Anneau de charge qui grandit au fil du cycle
        charge = (self.timer % self.pulse_interval) / self.pulse_interval
        ring_r = int(14 + charge * 22)
        ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        alpha = int(charge * 200)
        pygame.draw.circle(ring_surf, (0, 220, 255, alpha), (ring_r + 2, ring_r + 2), ring_r, 2)
        surface.blit(ring_surf, (self.rect.centerx - ring_r - 2, self.rect.centery - ring_r - 2))
        surface.blit(self.image, self.rect)


class ReflectorEnemy(Enemy):
    """Ennemi miroir - sa face inférieure renvoie les projectiles du joueur vers le bas."""
    def __init__(self, x, y, speed=1.8):
        super().__init__(x, y, speed, color=(200, 215, 225))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 3
        self._reflector_h = 12

    def _create_sprite(self):
        size = 42
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps métallique
        body = [(cx - 12, cy - 12), (cx + 12, cy - 12), (cx + 12, cy + 8), (cx - 12, cy + 8)]
        pygame.draw.polygon(surface, (165, 180, 192), body)
        pygame.draw.polygon(surface, (88, 103, 113), body, 2)

        # Highlights métalliques
        pygame.draw.line(surface, (212, 224, 232), (cx - 10, cy - 10), (cx + 10, cy - 10), 2)
        pygame.draw.line(surface, (128, 143, 153), (cx - 10, cy + 6), (cx + 10, cy + 6), 1)

        # Core
        pygame.draw.circle(surface, (143, 158, 168), (cx, cy - 2), 5)
        pygame.draw.circle(surface, (213, 224, 232), (cx - 1, cy - 3), 2)

        # Face miroir (bas - tournée vers le joueur)
        mirror_pts = [(cx - 15, cy + 8), (cx + 15, cy + 8), (cx + 13, cy + 18), (cx - 13, cy + 18)]
        pygame.draw.polygon(surface, (212, 238, 255), mirror_pts)
        for offset in (-7, -1, 5, 11):
            pygame.draw.line(surface, (255, 255, 255),
                             (cx + offset, cy + 10), (cx + offset + 2, cy + 16), 1)
        pygame.draw.polygon(surface, (138, 173, 213), mirror_pts, 2)

        return surface

    def get_reflector_rect(self):
        """Zone miroir en bas du sprite (face vers le joueur)."""
        return pygame.Rect(
            self.rect.left,
            self.rect.bottom - self._reflector_h,
            self.rect.width,
            self._reflector_h
        )

    def is_reflected(self, projectile_rect):
        """Renvoie True si le projectile touche la face miroir."""
        return self.get_reflector_rect().colliderect(projectile_rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Scintillement animé du miroir
        mr = self.get_reflector_rect()
        alpha = 60 + int(math.sin(self.timer * 0.12) * 40)
        glow = pygame.Surface((mr.width, mr.height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (200, 230, 255, alpha), (0, 0, mr.width, mr.height))
        surface.blit(glow, mr)


class BurstEnemy(Enemy):
    """Ennemi de rafale - descend normalement et tire périodiquement un éventail de 5 projectiles."""
    def __init__(self, x, y, speed=2.5):
        super().__init__(x, y, speed, color=(240, 100, 0))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 2
        self.burst_interval = 100
        self.burst_warning = 20
        self.burst_count = 5

    def _create_sprite(self):
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps principal
        pygame.draw.circle(surface, (188, 73, 0), (cx, cy - 2), 14)
        pygame.draw.circle(surface, (228, 113, 0), (cx, cy - 2), 10)

        # Triple canon vers le bas
        for offset in (-8, 0, 8):
            pygame.draw.rect(surface, (148, 53, 0), (cx + offset - 2, cy + 9, 4, 13))
            pygame.draw.rect(surface, (188, 73, 0), (cx + offset - 1, cy + 9, 2, 11))

        # Détail central
        pygame.draw.circle(surface, (255, 153, 0), (cx, cy - 4), 5)
        pygame.draw.circle(surface, (255, 218, 98), (cx - 1, cy - 5), 2)
        pygame.draw.circle(surface, (148, 53, 0), (cx, cy - 2), 14, 2)

        return surface

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed

        if self.timer % self.burst_interval == self.burst_interval - 1:
            ex, ey = self.rect.center
            spread_total = 70
            for i in range(self.burst_count):
                angle_deg = -spread_total / 2 + i * (spread_total / (self.burst_count - 1))
                angle_rad = math.radians(90 + angle_deg)
                enemy_projectiles.append(
                    EnemyProjectile(ex, ey, math.cos(angle_rad), math.sin(angle_rad), speed=5)
                )

    def draw(self, surface):
        cycle = self.timer % self.burst_interval
        if cycle >= self.burst_interval - self.burst_warning:
            charge = (cycle - (self.burst_interval - self.burst_warning)) / self.burst_warning
            warn_r = int(15 + charge * 12)
            warn_surf = pygame.Surface((warn_r * 2 + 4, warn_r * 2 + 4), pygame.SRCALPHA)
            alpha = int(charge * 200)
            pygame.draw.circle(warn_surf, (255, 160, 0, alpha),
                               (warn_r + 2, warn_r + 2), warn_r, 2)
            surface.blit(warn_surf,
                         (self.rect.centerx - warn_r - 2, self.rect.centery - warn_r - 2))
        surface.blit(self.image, self.rect)


class SpinnerEnemy(Enemy):
    """Ennemi tournoyeur - tourne sur lui-même et tire des projectiles en spirale."""
    def __init__(self, x, y, speed=1.5):
        super().__init__(x, y, speed, color=(0, 200, 180))
        self.base_image = self._create_sprite()
        self.image = self.base_image
        self.rect = self.base_image.get_rect(center=(x, y))
        self.hp = 2
        self.rotation_deg = 0
        self.fire_angle = 0.0   # Angle de tir courant (radians)
        self.fire_interval = 15

    def _create_sprite(self):
        size = 38
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Disque central
        pygame.draw.circle(surface, (0, 155, 145), (cx, cy), 14)
        pygame.draw.circle(surface, (0, 210, 195), (cx, cy), 9)

        # 4 lames de turbine
        for i in range(4):
            angle = i * math.pi / 2
            blade = [
                (cx + int(math.cos(angle) * 6),       cy + int(math.sin(angle) * 6)),
                (cx + int(math.cos(angle + 0.5) * 16), cy + int(math.sin(angle + 0.5) * 16)),
                (cx + int(math.cos(angle + 0.9) * 10), cy + int(math.sin(angle + 0.9) * 10)),
            ]
            pygame.draw.polygon(surface, (0, 230, 210), blade)
            pygame.draw.polygon(surface, (0, 140, 130), blade, 1)

        # Noyau
        pygame.draw.circle(surface, (150, 255, 240), (cx, cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)
        pygame.draw.circle(surface, (0, 120, 110), (cx, cy), 14, 2)

        return surface

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.rotation_deg = (self.rotation_deg + 4) % 360

        if self.timer % self.fire_interval == 0:
            ex, ey = self.rect.center
            enemy_projectiles.append(
                EnemyProjectile(ex, ey, math.cos(self.fire_angle), math.sin(self.fire_angle), speed=4)
            )
            self.fire_angle += math.pi / 6  # +30° à chaque tir -> spirale

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.base_image, self.rotation_deg)
        new_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, new_rect)


class OrbiterEnemy(Enemy):
    """Ennemi orbital - 3 orbes tournent autour de lui, bloquent les tirs et tirent sur le joueur."""
    def __init__(self, x, y, speed=1.5):
        super().__init__(x, y, speed, color=(100, 0, 150))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 4
        self.orb_radius = 32
        self.orb_angle = 0.0
        self.angular_speed = 0.04
        self.orb_fire_timer = 0
        self.orb_fire_interval = 75
        self.active_orb = 0  # Orbe qui tirera au prochain cycle

    def _create_sprite(self):
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps central sombre
        pygame.draw.circle(surface, (75, 0, 120), (cx, cy), 14)
        pygame.draw.circle(surface, (125, 0, 195), (cx, cy), 9)

        # Détails hexagonaux
        for i in range(6):
            angle = i * math.pi / 3
            px = cx + int(math.cos(angle) * 10)
            py = cy + int(math.sin(angle) * 10)
            pygame.draw.circle(surface, (175, 50, 250), (px, py), 2)

        pygame.draw.circle(surface, (220, 150, 255), (cx, cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)
        pygame.draw.circle(surface, (55, 0, 95), (cx, cy), 14, 2)

        return surface

    def get_orb_positions(self):
        positions = []
        for i in range(3):
            angle = self.orb_angle + i * (2 * math.pi / 3)
            x = self.rect.centerx + int(math.cos(angle) * self.orb_radius)
            y = self.rect.centery + int(math.sin(angle) * self.orb_radius)
            positions.append((x, y))
        return positions

    def get_orb_rects(self):
        d = 14
        return [pygame.Rect(px - d // 2, py - d // 2, d, d)
                for px, py in self.get_orb_positions()]

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.orb_angle += self.angular_speed
        self.orb_fire_timer += 1

        if self.orb_fire_timer >= self.orb_fire_interval:
            self.orb_fire_timer = 0
            positions = self.get_orb_positions()
            ox, oy = positions[self.active_orb]
            px, py = player_position
            dx = px - ox
            dy = py - oy
            dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
            enemy_projectiles.append(EnemyProjectile(ox, oy, dx / dist, dy / dist, speed=5))
            self.active_orb = (self.active_orb + 1) % 3

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        for px, py in self.get_orb_positions():
            pygame.draw.circle(surface, (175, 75, 255), (px, py), 7)
            pygame.draw.circle(surface, (218, 158, 255), (px - 1, py - 1), 3)
            pygame.draw.circle(surface, (55, 0, 95), (px, py), 7, 2)


class LaserDroneEnemy(Enemy):
    """Ennemi drone laser - balaye l'écran de gauche à droite avec un rayon laser continu."""
    def __init__(self, x, y, speed=0.5):
        super().__init__(x, y, speed, color=(220, 25, 25))
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 3
        self.sweep_time = 100   # frames pour un demi-balayage
        self.initial_delay = 60
        self.laser_active = False

    def _create_sprite(self):
        size = 46
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps plat style drone
        body = [(cx - 16, cy - 6), (cx + 16, cy - 6), (cx + 16, cy + 6), (cx - 16, cy + 6)]
        pygame.draw.polygon(surface, (195, 18, 18), body)
        pygame.draw.polygon(surface, (125, 10, 10), body, 2)

        # Cockpit
        pygame.draw.circle(surface, (255, 75, 75), (cx, cy), 7)
        pygame.draw.circle(surface, (255, 175, 175), (cx - 1, cy - 1), 3)

        # Ailes
        left_wing  = [(cx - 16, cy - 6), (cx - 22, cy - 14), (cx - 22, cy + 14), (cx - 16, cy + 6)]
        right_wing = [(cx + 16, cy - 6), (cx + 22, cy - 14), (cx + 22, cy + 14), (cx + 16, cy + 6)]
        pygame.draw.polygon(surface, (165, 14, 14), left_wing)
        pygame.draw.polygon(surface, (165, 14, 14), right_wing)
        pygame.draw.polygon(surface, (108, 8, 8), left_wing, 1)
        pygame.draw.polygon(surface, (108, 8, 8), right_wing, 1)

        # Émetteur laser
        pygame.draw.rect(surface, (255, 95, 95), (cx - 3, cy + 6, 6, 8))
        pygame.draw.circle(surface, (255, 48, 48), (cx, cy + 14), 4)

        return surface

    def get_laser_x(self):
        """Position X du laser (balayage sinusoïdal)."""
        return int((0.5 + 0.5 * math.sin(self.timer * math.pi / self.sweep_time)) * SCREEN_WIDTH)

    def get_laser_rect(self):
        """Rect de collision du faisceau (bande verticale étroite)."""
        lx = self.get_laser_x()
        return pygame.Rect(lx - 12, self.rect.bottom, 24, SCREEN_HEIGHT)

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        self.laser_active = self.timer >= self.initial_delay

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        if not self.laser_active:
            charge = self.timer / self.initial_delay
            if (self.timer // 8) % 2 == 0:
                ch_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.rect(ch_surf, (255, 80, 80, int(80 * charge)),
                                 (0, 0, self.rect.width, self.rect.height), 3)
                surface.blit(ch_surf, self.rect)
            return

        lx = self.get_laser_x()
        beam_y = self.rect.bottom
        beam_h = SCREEN_HEIGHT - beam_y + 10
        # Lueur multicouche
        for width, alpha in ((10, 35), (6, 75), (3, 175), (2, 255)):
            ls = pygame.Surface((width * 2, beam_h), pygame.SRCALPHA)
            r = 255 if width <= 3 else 200
            pygame.draw.rect(ls, (r, 28, 28, alpha), (0, 0, width * 2, beam_h))
            surface.blit(ls, (lx - width, beam_y))
        pygame.draw.circle(surface, (255, 100, 50), (lx, beam_y), 5)


class ArmoredEnemy(Enemy):
    """Ennemi blindé - les plaques de blindage absorbent les impacts avant que les PV soient affectés."""
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, speed, color=(95, 105, 115))
        self.hp = 3
        self.armor = 3
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 44
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Corps hexagonal central
        hex_pts = [
            (cx + int(math.cos(i * math.pi / 3) * 12),
             cy + int(math.sin(i * math.pi / 3) * 12))
            for i in range(6)
        ]
        pygame.draw.polygon(surface, (88, 98, 108), hex_pts)
        pygame.draw.polygon(surface, (130, 143, 153), hex_pts, 2)

        # Noyau
        pygame.draw.circle(surface, (148, 163, 173), (cx, cy), 6)
        pygame.draw.circle(surface, (208, 220, 228), (cx - 1, cy - 1), 2)

        return surface

    def take_hit(self):
        """Gère l'impact. Retourne True si l'ennemi est détruit."""
        if self.armor > 0:
            self.armor -= 1
            return False
        else:
            self.hp -= 1
            return self.hp <= 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        cx, cy = self.rect.center

        # Plaques de blindage restantes (dessinées dynamiquement)
        plate_angles = [i * (2 * math.pi / 3) for i in range(3)]
        for i in range(self.armor):
            angle = plate_angles[i]
            px = cx + int(math.cos(angle) * 19)
            py = cy + int(math.sin(angle) * 19)
            plate_pts = [
                (px + int(math.cos(angle) * 9),       py + int(math.sin(angle) * 9)),
                (px + int(math.cos(angle + 1.2) * 7), py + int(math.sin(angle + 1.2) * 7)),
                (px + int(math.cos(angle + math.pi) * 9), py + int(math.sin(angle + math.pi) * 9)),
                (px + int(math.cos(angle - 1.2) * 7), py + int(math.sin(angle - 1.2) * 7)),
            ]
            pygame.draw.polygon(surface, (118, 132, 142), plate_pts)
            pygame.draw.polygon(surface, (198, 212, 222), plate_pts, 1)

        # Indicateur d'armure restante (points au-dessus)
        for k in range(self.armor):
            pygame.draw.circle(surface, (178, 198, 208),
                               (self.rect.left + 5 + k * 9, self.rect.top - 7), 3)
        for k in range(3 - self.armor):
            pygame.draw.circle(surface, (60, 70, 80),
                               (self.rect.left + 5 + (self.armor + k) * 9, self.rect.top - 7), 3)


class ClonerEnemy(Enemy):
    """Ennemi clonateur - crée un décoy de lui-même pour semer la confusion."""
    def __init__(self, x, y, speed=2, is_decoy=False):
        super().__init__(x, y, speed, color=(195, 195, 45))
        self.is_decoy = is_decoy
        self.base_image = self._create_sprite()
        self.image = self.base_image
        self.rect = self.base_image.get_rect(center=(x, y))
        self.hp = 1 if is_decoy else 3
        self.has_cloned = is_decoy  # Les décoys ne clonent pas
        self.clone_delay = 60

    def _create_sprite(self):
        size = 36
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        pygame.draw.circle(surface, (165, 165, 28), (cx, cy), 13)
        pygame.draw.circle(surface, (218, 218, 75), (cx, cy), 8)

        for i in range(6):
            angle = i * math.pi / 3
            px = cx + int(math.cos(angle) * 9)
            py = cy + int(math.sin(angle) * 9)
            pygame.draw.circle(surface, (238, 238, 98), (px, py), 2)

        pygame.draw.circle(surface, (255, 255, 148), (cx, cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 1, cy - 1), 1)
        pygame.draw.circle(surface, (128, 128, 18), (cx, cy), 13, 2)

        # Petit marqueur bleu discret sur le vrai (visible si on cherche)
        if not self.is_decoy:
            pygame.draw.circle(surface, (50, 100, 255), (cx + 7, cy - 7), 2)

        return surface

    def clone(self):
        """Retourne un décoy positionné à côté."""
        offset_x = random.choice((-85, 85))
        return ClonerEnemy(self.rect.centerx + offset_x, self.rect.centery,
                           speed=3, is_decoy=True)

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        if self.is_decoy:
            # Légère oscillation pour être légèrement différent du vrai
            self.rect.x = self.start_x + int(math.sin(self.timer * 0.06) * 20)

    def draw(self, surface):
        if self.is_decoy:
            decoy_surf = self.base_image.copy()
            decoy_surf.set_alpha(205)
            surface.blit(decoy_surf, self.rect)
        else:
            surface.blit(self.base_image, self.rect)

        # Halo d'avertissement avant le clonage
        if not self.is_decoy and not self.has_cloned and self.timer >= self.clone_delay - 25:
            charge = (self.timer - (self.clone_delay - 25)) / 25
            warn = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            alpha = int(charge * 160)
            pygame.draw.rect(warn, (255, 255, 100, alpha),
                             (0, 0, self.rect.width + 12, self.rect.height + 12), 2)
            surface.blit(warn, (self.rect.x - 6, self.rect.y - 6))


class HealerEnemy(Enemy):
    """Ennemi soigneur — émet une aura qui régénère les PV des ennemis proches."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 2
        self.heal_interval = 90
        self.heal_radius = 100
        self.heal_amount = 1
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.base_image = self.image.copy()
        self.aura_pulse = 0

    def _create_sprite(self):
        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (100, 220, 100), (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(surf, (60, 180, 60), (size // 2, size // 2), size // 2 - 2, 2)
        cx, cy = size // 2, size // 2
        pygame.draw.rect(surf, (255, 255, 255), (cx - 3, cy - 10, 6, 20))
        pygame.draw.rect(surf, (255, 255, 255), (cx - 10, cy - 3, 20, 6))
        return surf

    def update(self, enemies):
        self.timer += 1
        self.rect.y += self.speed
        self.aura_pulse = (self.aura_pulse + 1) % 90
        if self.timer % self.heal_interval == 0:
            for enemy in enemies:
                if enemy is self:
                    continue
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                if math.hypot(dx, dy) <= self.heal_radius:
                    max_hp = getattr(enemy, 'max_hp', enemy.hp + 1)
                    enemy.hp = min(enemy.hp + self.heal_amount, max_hp)

    def draw(self, surface):
        aura_alpha = int(80 + 40 * math.sin(self.aura_pulse * 0.07 * math.pi))
        aura_r = self.heal_radius
        aura_surf = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (100, 220, 100, aura_alpha),
                           (aura_r + 2, aura_r + 2), aura_r, 1)
        surface.blit(aura_surf,
                     (self.rect.centerx - aura_r - 2, self.rect.centery - aura_r - 2))
        surface.blit(self.image, self.rect)


class MagnetEnemy(Enemy):
    """Ennemi magnétique — attire les projectiles du joueur vers lui."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 2
        self.magnet_radius = 120
        self.magnet_force = 0.12
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.base_image = self.image.copy()
        self.pulse_timer = 0

    def _create_sprite(self):
        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (70, 100, 200), (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(surf, (40, 60, 150), (size // 2, size // 2), size // 2 - 2, 2)
        pygame.draw.arc(surf, (220, 50, 50), (4, 4, size - 8, size - 8), 0, math.pi, 3)
        pygame.draw.arc(surf, (50, 100, 220), (4, 4, size - 8, size - 8), math.pi, 2 * math.pi, 3)
        font = pygame.font.SysFont(None, 14)
        n_label = font.render("N", True, (255, 80, 80))
        s_label = font.render("S", True, (80, 150, 255))
        surf.blit(n_label, (size // 2 - 4, 5))
        surf.blit(s_label, (size // 2 - 4, size - 16))
        return surf

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        self.pulse_timer = (self.pulse_timer + 1) % 60

    def apply_magnet(self, projectiles):
        """Attire les projectiles du joueur vers soi."""
        ex, ey = self.rect.centerx, self.rect.centery
        for proj in projectiles:
            dx = ex - proj.rect.centerx
            dy = ey - proj.rect.centery
            dist = math.hypot(dx, dy)
            if 0 < dist < self.magnet_radius:
                pull = self.magnet_force * (1 - dist / self.magnet_radius)
                proj.rect.x += int(dx / dist * pull * dist)
                proj.rect.y += int(dy / dist * pull * dist)

    def draw(self, surface):
        for i in range(1, 4):
            r = int(self.magnet_radius * i / 4)
            alpha = int(50 - i * 10 + 20 * math.sin(self.pulse_timer * 0.1 + i))
            alpha = max(10, min(alpha, 70))
            ring_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (70, 100, 200, alpha),
                               (r + 2, r + 2), r, 1)
            surface.blit(ring_surf,
                         (self.rect.centerx - r - 2, self.rect.centery - r - 2))
        surface.blit(self.image, self.rect)


class OverchargedEnemy(Enemy):
    """Ennemi surchargé — devient plus rapide et dangereux à mesure qu'il perd des PV."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.max_hp = 4
        self.hp = 4
        self.fire_timer = 0
        self.image = self._create_sprite(phase=0)
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self, phase=0):
        size = 44
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = [(200, 200, 50), (230, 200, 30), (255, 180, 0), (255, 100, 0)]
        body_color = colors[min(phase, 3)]
        pts = []
        for i in range(6):
            angle = math.radians(i * 60 - 30)
            pts.append((size // 2 + int((size // 2 - 3) * math.cos(angle)),
                        size // 2 + int((size // 2 - 3) * math.sin(angle))))
        pygame.draw.polygon(surf, body_color, pts)
        pygame.draw.polygon(surf, (255, 255, 255), pts, 2)
        bolt = [(22, 10), (16, 22), (21, 22), (15, 34), (28, 20), (22, 20)]
        bolt_color = (255, 255, 100) if phase < 3 else (255, 80, 0)
        pygame.draw.polygon(surf, bolt_color, bolt)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        phase = self.max_hp - self.hp
        self.rect.y += self.speed + phase * 0.6
        fire_interval = max(15, 80 - phase * 20)
        num_shots = 1 + phase
        self.fire_timer += 1
        if self.fire_timer >= fire_interval:
            self.fire_timer = 0
            for i in range(num_shots):
                angle_offset = (i - (num_shots - 1) / 2) * 18
                angle = math.radians(90 + angle_offset)
                dx = math.cos(angle)
                dy = math.sin(angle)
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx, self.rect.bottom, dx, dy,
                                    speed=4 + phase))
        center = self.rect.center
        self.image = self._create_sprite(phase)
        self.rect = self.image.get_rect(center=center)

    def draw(self, surface):
        phase = self.max_hp - self.hp
        surface.blit(self.image, self.rect)
        if phase >= 2:
            for _ in range(phase * 2):
                sx = self.rect.centerx + random.randint(-18, 18)
                sy = self.rect.centery + random.randint(-18, 18)
                r = random.randint(1, 3)
                pygame.draw.circle(surface, (255, 220, 50), (sx, sy), r)


class SentinelEnemy(Enemy):
    """Ennemi sentinelle — s'arrête en haut de l'écran et tourne en tirant dans 3 directions."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 5
        self.target_y = 200
        self.halted = False
        self.rotation = 0.0
        self.rotation_speed = 1.5
        self.fire_timer = 0
        self.fire_interval = 70
        self.base_image = self._create_sprite()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 46
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pts = []
        for i in range(8):
            angle = math.radians(i * 45)
            pts.append((size // 2 + int((size // 2 - 3) * math.cos(angle)),
                        size // 2 + int((size // 2 - 3) * math.sin(angle))))
        pygame.draw.polygon(surf, (20, 30, 80), pts)
        pygame.draw.polygon(surf, (80, 100, 200), pts, 2)
        for i in range(3):
            angle = math.radians(i * 120 - 90)
            tx = size // 2 + int(14 * math.cos(angle))
            ty = size // 2 + int(14 * math.sin(angle))
            pygame.draw.circle(surf, (100, 130, 220), (tx, ty), 5)
            pygame.draw.circle(surf, (180, 200, 255), (tx, ty), 5, 1)
        pygame.draw.circle(surf, (150, 180, 255), (size // 2, size // 2), 4)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        if not self.halted:
            self.rect.y += self.speed
            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.halted = True
        if self.halted:
            self.rotation = (self.rotation + self.rotation_speed) % 360
        center = self.rect.center
        self.image = pygame.transform.rotate(self.base_image, -self.rotation)
        self.rect = self.image.get_rect(center=center)
        self.fire_timer += 1
        if self.halted and self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            for i in range(3):
                angle = math.radians(self.rotation + i * 120)
                dx = math.cos(angle)
                dy = math.sin(angle)
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, speed=4))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class EchoEnemy(Enemy):
    """Ennemi écho — riposte avec 3 projectiles chaque fois qu'il est touché."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2.5)
        self.hp = 3
        self.hit_flash = 0
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.base_image = self.image.copy()

    def _create_sprite(self):
        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.ellipse(surf, (210, 140, 220), (2, cy - 14, 16, 28))
        pygame.draw.ellipse(surf, (210, 140, 220), (cx + 2, cy - 14, 16, 28))
        pygame.draw.circle(surf, (180, 80, 200), (cx, cy), 8)
        pygame.draw.circle(surf, (230, 180, 240), (cx, cy), 8, 1)
        return surf

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def on_hit(self, player_position, enemy_projectiles):
        """Riposte vers le joueur avec 3 projectiles en éventail."""
        self.hit_flash = 8
        px, py = player_position
        ex, ey = self.rect.centerx, self.rect.centery
        base_angle = math.atan2(py - ey, px - ex)
        for offset in (-25, 0, 25):
            angle = base_angle + math.radians(offset)
            dx = math.cos(angle)
            dy = math.sin(angle)
            enemy_projectiles.append(EnemyProjectile(ex, ey, dx, dy, speed=5))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.hit_flash > 0:
            flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, min(200, self.hit_flash * 25)))
            surface.blit(flash_surf, self.rect)


class ChargerEnemy(Enemy):
    """Ennemi chargeur — descend, s'aligne avec le joueur puis fonce horizontalement."""

    PHASE_DESCENT = 0
    PHASE_ALIGN   = 1
    PHASE_CHARGE  = 2

    def __init__(self, x, y):
        super().__init__(x, y, speed=3)
        self.hp = 2
        self.phase = self.PHASE_DESCENT
        self.phase_timer = 0
        self.charge_dx = 1
        self.charge_speed = 12
        self.is_charging = False
        self.image = self._create_sprite(1)
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self, direction=1):
        w, h = 44, 32
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if direction >= 0:
            pts = [(4, 0), (40, h // 2), (4, h), (14, h // 2)]
        else:
            pts = [(40, 0), (4, h // 2), (40, h), (30, h // 2)]
        pygame.draw.polygon(surf, (255, 140, 0), pts)
        pygame.draw.polygon(surf, (255, 210, 60), pts, 2)
        return surf

    def update(self, player_position):
        self.timer += 1
        self.phase_timer += 1

        if self.phase == self.PHASE_DESCENT:
            self.rect.y += self.speed
            if self.phase_timer >= 80:
                self.phase = self.PHASE_ALIGN
                self.phase_timer = 0

        elif self.phase == self.PHASE_ALIGN:
            px = player_position[0]
            dx = px - self.rect.centerx
            move = max(-4, min(4, dx))
            self.rect.x += move
            if abs(dx) < 20 or self.phase_timer >= 90:
                self.charge_dx = 1 if dx >= 0 else -1
                center = self.rect.center
                self.image = self._create_sprite(self.charge_dx)
                self.rect = self.image.get_rect(center=center)
                self.phase = self.PHASE_CHARGE
                self.phase_timer = 0
                self.is_charging = True

        elif self.phase == self.PHASE_CHARGE:
            self.rect.x += self.charge_dx * self.charge_speed
            # Sortie horizontale — déclenche la suppression hors-écran
            if self.rect.right < -20 or self.rect.left > SCREEN_WIDTH + 20:
                self.rect.y = SCREEN_HEIGHT + 100

    def draw(self, surface):
        if self.phase == self.PHASE_ALIGN and self.phase_timer % 20 < 10:
            warn_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            warn_surf.fill((255, 200, 0, 80))
            surface.blit(warn_surf, self.rect)
        surface.blit(self.image, self.rect)


class ShadowEnemy(Enemy):
    """Ennemi ombre — se positionne en miroir du joueur et tire vers le bas."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 4
        self.target_y = 160
        self.halted = False
        self.fire_timer = 0
        self.fire_interval = 65
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (40, 50, 80), (8, 8, 24, 24))
        pygame.draw.ellipse(surf, (120, 140, 200), (8, 8, 24, 24), 2)
        pts_left  = [(0, 34), (8, 20), (18, 28)]
        pts_right = [(40, 34), (32, 20), (22, 28)]
        pygame.draw.polygon(surf, (60, 80, 120), pts_left)
        pygame.draw.polygon(surf, (60, 80, 120), pts_right)
        pygame.draw.circle(surf, (100, 160, 255), (size // 2, size // 2), 5)
        pygame.draw.circle(surf, (200, 220, 255), (size // 2, size // 2), 2)
        return surf

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        if not self.halted:
            self.rect.y += self.speed
            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.halted = True
        else:
            px = player_position[0]
            dx = px - self.rect.centerx
            self.rect.x += max(-5, min(5, dx))
            self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

        self.fire_timer += 1
        if self.halted and self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            enemy_projectiles.append(
                EnemyProjectile(self.rect.centerx, self.rect.bottom, 0, 1, speed=5))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class DrainerEnemy(Enemy):
    """Ennemi draineur — absorbe les projectiles du joueur et tire une salve tous les 3 impacts."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 6
        self.charge = 0
        self.max_charge = 3
        self.fire_flash = 0
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (100, 0, 180), (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(surf, (160, 60, 255), (size // 2, size // 2), size // 2 - 2, 2)
        for i in range(3):
            a0 = math.radians(i * 120)
            a1 = math.radians(i * 120 + 80)
            pygame.draw.arc(surf, (200, 100, 255),
                            (6, 6, size - 12, size - 12), a0, a1, 2)
        return surf

    def absorb_hit(self, player_position, enemy_projectiles):
        """Appelé à la place de hp -= 1. Absorbe et tire si chargé. Retourne True si mort."""
        self.hp -= 1
        self.charge += 1
        if self.charge >= self.max_charge:
            self.charge = 0
            self.fire_flash = 12
            px, py = player_position
            ex, ey = self.rect.centerx, self.rect.centery
            base_angle = math.atan2(py - ey, px - ex)
            for offset in (-15, 0, 15):
                angle = base_angle + math.radians(offset)
                enemy_projectiles.append(
                    EnemyProjectile(ex, ey, math.cos(angle), math.sin(angle), speed=9))
        return self.hp <= 0

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        if self.fire_flash > 0:
            self.fire_flash -= 1

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Indicateurs de charge
        for i in range(self.charge):
            a0 = math.radians(i * 120 - 30)
            a1 = math.radians(i * 120 + 30)
            csf = pygame.Surface((52, 52), pygame.SRCALPHA)
            pygame.draw.arc(csf, (220, 80, 255, 200), (2, 2, 48, 48), a0, a1, 3)
            surface.blit(csf, (self.rect.centerx - 26, self.rect.centery - 26))
        if self.fire_flash > 0:
            flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((200, 100, 255, min(180, self.fire_flash * 15)))
            surface.blit(flash_surf, self.rect)


class SwarmEnemy(Enemy):
    """Minion en essaim — petit, rapide, se dirige vers le joueur en groupe."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=5)
        self.hp = 1
        self.vx = 0.0
        self.vy = float(self.speed)
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 22
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pts = [(size // 2, size - 2), (2, 2), (size - 2, 2)]
        pygame.draw.polygon(surf, (150, 255, 50), pts)
        pygame.draw.polygon(surf, (200, 255, 100), pts, 1)
        return surf

    def update(self, player_position):
        self.timer += 1
        px, py = player_position
        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx += (dx / dist) * 0.05
            self.vy += (dy / dist) * 0.05
        spd = math.hypot(self.vx, self.vy)
        if spd > 6:
            self.vx = self.vx / spd * 6
            self.vy = self.vy / spd * 6
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, surface):
        angle = math.degrees(math.atan2(-self.vy, self.vx)) - 90
        rotated = pygame.transform.rotate(self.image, angle)
        rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rect)


class GridEnemy(Enemy):
    """Ennemi grille — s'arrête en haut et alterne tirs en croix et en diagonale."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 3
        self.target_y = 220
        self.halted = False
        self.fire_timer = 0
        self.fire_interval = 80
        self.volley = 0  # 0 = croix, 1 = diagonale
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 42
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 140, 140), (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(surf, (0, 220, 220), (size // 2, size // 2), size // 2 - 2, 2)
        cx, cy = size // 2, size // 2
        pygame.draw.line(surf, (0, 220, 220), (cx, 4), (cx, size - 4), 1)
        pygame.draw.line(surf, (0, 220, 220), (4, cy), (size - 4, cy), 1)
        pygame.draw.line(surf, (0, 160, 160), (6, 6), (size - 6, size - 6), 1)
        pygame.draw.line(surf, (0, 160, 160), (size - 6, 6), (6, size - 6), 1)
        pygame.draw.circle(surf, (0, 255, 255), (cx, cy), 4)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        if not self.halted:
            self.rect.y += self.speed
            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.halted = True
        self.fire_timer += 1
        if self.halted and self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            d = 1 / math.sqrt(2)
            dirs = [(0, -1), (0, 1), (1, 0), (-1, 0)] if self.volley == 0 \
                else [(d, -d), (d, d), (-d, d), (-d, -d)]
            for dx, dy in dirs:
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, speed=4))
            self.volley = 1 - self.volley

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        cx, cy = self.rect.centerx, self.rect.centery
        # Indicateur du prochain type de tir
        d = 16
        if self.volley == 0:
            pygame.draw.line(surface, (0, 180, 180), (cx, cy - d), (cx, cy + d), 1)
            pygame.draw.line(surface, (0, 180, 180), (cx - d, cy), (cx + d, cy), 1)
        else:
            pygame.draw.line(surface, (0, 140, 140), (cx - d, cy - d), (cx + d, cy + d), 1)
            pygame.draw.line(surface, (0, 140, 140), (cx + d, cy - d), (cx - d, cy + d), 1)


class FreezerEnemy(Enemy):
    """Tire 6 projectiles en flocon de neige toutes les 80 frames."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 2
        self.fire_timer = 0
        self.fire_interval = 80
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 38
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.circle(surf, (150, 220, 255), (cx, cy), size // 2 - 2)
        pygame.draw.circle(surf, (200, 240, 255), (cx, cy), size // 2 - 2, 2)
        for i in range(6):
            angle = math.radians(i * 60)
            x2 = cx + int((size // 2 - 3) * math.cos(angle))
            y2 = cy + int((size // 2 - 3) * math.sin(angle))
            pygame.draw.line(surf, (220, 245, 255), (cx, cy), (x2, y2), 2)
            for t in (0.5, 0.75):
                bx = cx + int((size // 2 - 3) * t * math.cos(angle))
                by = cy + int((size // 2 - 3) * t * math.sin(angle))
                perp = angle + math.pi / 2
                pygame.draw.line(surf, (190, 230, 255),
                                 (bx + int(4 * math.cos(perp)), by + int(4 * math.sin(perp))),
                                 (bx - int(4 * math.cos(perp)), by - int(4 * math.sin(perp))), 1)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            for i in range(6):
                angle = math.radians(i * 60)
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx, self.rect.centery,
                                    math.cos(angle), math.sin(angle), speed=3))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class DiveEnemy(Enemy):
    """Mémorise la position du joueur puis plonge dessus à grande vitesse."""

    PHASE_TRACK = 0
    PHASE_AIM   = 1
    PHASE_DIVE  = 2

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 1
        self.phase = self.PHASE_TRACK
        self.phase_timer = 0
        self.dive_dx = 0.0
        self.dive_dy = 1.0
        self.dive_speed = 13
        self.is_diving = False
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        w, h = 28, 40
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pts = [(w // 2, h - 2), (2, h // 3), (w // 2, h // 4), (w - 2, h // 3)]
        pygame.draw.polygon(surf, (200, 20, 20), pts)
        pygame.draw.polygon(surf, (255, 80, 80), pts, 2)
        return surf

    def update(self, player_position):
        self.timer += 1
        self.phase_timer += 1
        if self.phase == self.PHASE_TRACK:
            self.rect.y += self.speed
            self.rect.x += max(-2, min(2, player_position[0] - self.rect.centerx))
            if self.phase_timer >= 60:
                self.phase = self.PHASE_AIM
                self.phase_timer = 0
        elif self.phase == self.PHASE_AIM:
            if self.phase_timer >= 20:
                px, py = player_position
                dx = px - self.rect.centerx
                dy = py - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.dive_dx = dx / dist
                    self.dive_dy = dy / dist
                self.phase = self.PHASE_DIVE
                self.phase_timer = 0
                self.is_diving = True
        elif self.phase == self.PHASE_DIVE:
            self.rect.x += int(self.dive_dx * self.dive_speed)
            self.rect.y += int(self.dive_dy * self.dive_speed)
            if self.rect.right < -20 or self.rect.left > SCREEN_WIDTH + 20:
                self.rect.y = SCREEN_HEIGHT + 100

    def draw(self, surface):
        if self.phase == self.PHASE_AIM and self.phase_timer % 8 < 4:
            flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 100))
            surface.blit(flash, self.rect)
        surface.blit(self.image, self.rect)


class ScatterEnemy(Enemy):
    """Tire 8 projectiles dirigés vers le joueur avec grand écart toutes les 65 frames."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 2
        self.fire_timer = 0
        self.fire_interval = 65
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 38
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.circle(surf, (210, 120, 0), (cx, cy), 9)
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = cx + int(9 * math.cos(angle))
            y1 = cy + int(9 * math.sin(angle))
            x2 = cx + int(17 * math.cos(angle))
            y2 = cy + int(17 * math.sin(angle))
            pygame.draw.line(surf, (255, 150, 30), (x1, y1), (x2, y2), 2)
        pygame.draw.circle(surf, (255, 170, 50), (cx, cy), 6)
        return surf

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            px, py = player_position
            base = math.atan2(py - self.rect.centery, px - self.rect.centerx)
            for i in range(8):
                angle = base + math.radians(-52 + i * 104 / 7)
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx, self.rect.centery,
                                    math.cos(angle), math.sin(angle),
                                    speed=random.uniform(2.5, 4.0)))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class AnchorEnemy(Enemy):
    """Ennemi très lourd — descend lentement, HP=8, affiche une barre de vie."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=0.7)
        self.hp = 8
        self.max_hp = 8
        self.fire_timer = 0
        self.fire_interval = 120
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        w, h = 56, 56
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        pts = []
        for i in range(6):
            angle = math.radians(i * 60)
            pts.append((cx + int((w // 2 - 3) * math.cos(angle)),
                        cy + int((h // 2 - 3) * math.sin(angle))))
        pygame.draw.polygon(surf, (80, 90, 100), pts)
        pygame.draw.polygon(surf, (150, 160, 170), pts, 3)
        for i in range(6):
            angle = math.radians(i * 60)
            px2 = cx + int((w // 2 - 10) * math.cos(angle))
            py2 = cy + int((h // 2 - 10) * math.sin(angle))
            pygame.draw.circle(surf, (110, 120, 130), (px2, py2), 4)
        pygame.draw.circle(surf, (60, 70, 80), (cx, cy), 10)
        pygame.draw.circle(surf, (160, 170, 180), (cx, cy), 10, 2)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            for ox in (-18, 18):
                enemy_projectiles.append(
                    EnemyProjectile(self.rect.centerx + ox, self.rect.bottom,
                                    0, 1, speed=2))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        bar_w = 50
        bar_x = self.rect.centerx - bar_w // 2
        bar_y = self.rect.bottom + 4
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (50, 60, 70), (bar_x, bar_y, bar_w, 5))
        pygame.draw.rect(surface, (140, 155, 165),
                         (bar_x, bar_y, int(bar_w * ratio), 5))


class MirageEnemy(Enemy):
    """Crée 2 mirages semi-transparents et plus rapides après 80 frames."""

    def __init__(self, x, y, is_mirage=False):
        super().__init__(x, y, speed=4 if is_mirage else 2)
        self.hp = 1 if is_mirage else 3
        self.is_mirage = is_mirage
        self.has_spawned = False
        self.spawn_delay = 80
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.base_image = self.image.copy()

    def _create_sprite(self):
        size = 36
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.circle(surf, (170, 110, 210), (cx, cy), size // 2 - 2)
        pygame.draw.circle(surf, (220, 160, 255), (cx, cy), size // 2 - 2, 2)
        pygame.draw.ellipse(surf, (200, 160, 230), (cx - 12, cy - 4, 24, 8))
        pygame.draw.ellipse(surf, (200, 160, 230), (cx - 4, cy - 12, 8, 24))
        return surf

    def get_mirages(self):
        if self.is_mirage or self.has_spawned:
            return []
        m1 = MirageEnemy(self.rect.centerx - 70, self.rect.centery, is_mirage=True)
        m2 = MirageEnemy(self.rect.centerx + 70, self.rect.centery, is_mirage=True)
        return [m1, m2]

    def update(self):
        self.timer += 1
        self.rect.y += self.speed
        if self.is_mirage:
            self.rect.x = self.start_x + int(math.sin(self.timer * 0.1) * 35)

    def draw(self, surface):
        img = self.base_image.copy()
        if self.is_mirage:
            img.set_alpha(150)
        surface.blit(img, self.rect)
        if not self.is_mirage and not self.has_spawned and self.timer >= self.spawn_delay - 20:
            charge = (self.timer - (self.spawn_delay - 20)) / 20
            warn = pygame.Surface((self.rect.width + 14, self.rect.height + 14), pygame.SRCALPHA)
            pygame.draw.rect(warn, (220, 160, 255, int(charge * 150)),
                             (0, 0, self.rect.width + 14, self.rect.height + 14), 2)
            surface.blit(warn, (self.rect.x - 7, self.rect.y - 7))


class RipperEnemy(Enemy):
    """Se déplace latéralement en rebondissant et tire dans sa direction de déplacement."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=1.5)
        self.hp = 2
        self.lateral_dir = 1
        self.lateral_speed = 4
        self.fire_timer = 0
        self.fire_interval = 50
        self.image = self._create_sprite(1)
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self, direction=1):
        size = 38
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.circle(surf, (30, 180, 30), (cx, cy), size // 2 - 2)
        pygame.draw.circle(surf, (100, 255, 100), (cx, cy), size // 2 - 2, 2)
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            x2 = cx + int((size // 2 - 2) * math.cos(angle))
            y2 = cy + int((size // 2 - 2) * math.sin(angle))
            pygame.draw.line(surf, (150, 255, 80), (cx, cy), (x2, y2), 2)
        pygame.draw.circle(surf, (80, 220, 80), (cx, cy), 5)
        # Direction arrow
        if direction > 0:
            pts = [(cx + 3, cy - 5), (cx + 11, cy), (cx + 3, cy + 5)]
        else:
            pts = [(cx - 3, cy - 5), (cx - 11, cy), (cx - 3, cy + 5)]
        pygame.draw.polygon(surf, (200, 255, 150), pts)
        return surf

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.rect.x += self.lateral_dir * self.lateral_speed
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.lateral_dir *= -1
            center = self.rect.center
            self.image = self._create_sprite(self.lateral_dir)
            self.rect = self.image.get_rect(center=center)
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            enemy_projectiles.append(
                EnemyProjectile(self.rect.centerx, self.rect.centery,
                                self.lateral_dir, 0.4, speed=5))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class ChainEnemy(Enemy):
    """En binôme — la mort de l'un déclenche l'explosion de l'autre."""

    def __init__(self, x, y):
        super().__init__(x, y, speed=2)
        self.hp = 2
        self.partner = None  # Lien établi après création
        self.fire_timer = 0
        self.image = self._create_sprite()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_sprite(self):
        size = 38
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.circle(surf, (180, 150, 0), (cx, cy), size // 2 - 2)
        pygame.draw.circle(surf, (255, 220, 0), (cx, cy), size // 2 - 2, 2)
        pygame.draw.circle(surf, (220, 180, 0), (cx, cy), 8, 2)
        pygame.draw.line(surf, (255, 220, 0), (cx - 8, cy), (cx + 8, cy), 2)
        pygame.draw.line(surf, (255, 220, 0), (cx, cy - 8), (cx, cy + 8), 1)
        return surf

    def chain_explode(self, enemy_projectiles):
        """Explose en 6 projectiles lors de la réaction en chaîne."""
        for i in range(6):
            angle = math.radians(i * 60)
            enemy_projectiles.append(
                EnemyProjectile(self.rect.centerx, self.rect.centery,
                                math.cos(angle), math.sin(angle), speed=4))

    def update(self, enemy_projectiles):
        self.timer += 1
        self.rect.y += self.speed
        self.fire_timer += 1
        if self.fire_timer >= 100:
            self.fire_timer = 0
            enemy_projectiles.append(
                EnemyProjectile(self.rect.centerx, self.rect.bottom, 0, 1, speed=4))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.partner and self.partner.hp > 0:
            pygame.draw.line(surface, (200, 160, 0),
                             self.rect.center, self.partner.rect.center, 1)

