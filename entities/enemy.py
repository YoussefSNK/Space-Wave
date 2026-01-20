import pygame

from config import RED, CYAN, ORANGE
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
