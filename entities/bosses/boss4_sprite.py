import pygame
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class Boss4Sprite:
    """Gere tout le rendu visuel du Boss 4 (sprites, aura, anneaux, effets)"""

    def __init__(self, size):
        self.size = size

    def create_sprite(self):
        """Cree un sprite procedural pour le Boss 4 - Soleil/Etoile divine"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        outer_tip_radius = 78

        for i in range(12):
            angle = math.radians(30 * i)
            inner_radius = 40
            outer_radius = 70
            x1 = center + math.cos(angle) * inner_radius
            y1 = center + math.sin(angle) * inner_radius
            x2 = center + math.cos(angle) * outer_radius
            y2 = center + math.sin(angle) * outer_radius
            pygame.draw.line(surf, (255, 200, 0), (x1, y1), (x2, y2), 4)

        pygame.draw.circle(surf, (180, 120, 0), (center, center), 45)
        pygame.draw.circle(surf, (255, 200, 50), (center, center), 40)
        pygame.draw.circle(surf, (255, 215, 0), (center, center), 45, 3)

        # Points entre les branches + traits de jointure vers les extremites
        for i in range(12):
            mid_angle = math.radians(30 * i + 15)
            px = center + math.cos(mid_angle) * 45
            py = center + math.sin(mid_angle) * 45

            angle_a = math.radians(30 * i)
            tip_ax = center + math.cos(angle_a) * 70
            tip_ay = center + math.sin(angle_a) * 70

            angle_b = math.radians(30 * (i + 1))
            tip_bx = center + math.cos(angle_b) * 70
            tip_by = center + math.sin(angle_b) * 70

            pygame.draw.line(surf, (255, 200, 0), (px, py), (tip_ax, tip_ay), 3)
            pygame.draw.line(surf, (255, 200, 0), (px, py), (tip_bx, tip_by), 3)
            pygame.draw.circle(surf, (255, 200, 0), (int(px), int(py)), 3)

        # Traits orange du centre vers les branches etendues
        for i in range(12):
            angle = math.radians(30 * i)
            ext_x = center + math.cos(angle) * outer_tip_radius
            ext_y = center + math.sin(angle) * outer_tip_radius
            pygame.draw.line(surf, (255, 127, 39), (center, center), (ext_x, ext_y), 3)

        # Zigzag exterieur orange
        outer_point_radius = 60
        for i in range(12):
            mid_angle = math.radians(30 * i + 15)
            opx = center + math.cos(mid_angle) * outer_point_radius
            opy = center + math.sin(mid_angle) * outer_point_radius

            angle_a = math.radians(30 * i)
            otip_ax = center + math.cos(angle_a) * outer_tip_radius
            otip_ay = center + math.sin(angle_a) * outer_tip_radius

            angle_b = math.radians(30 * (i + 1))
            otip_bx = center + math.cos(angle_b) * outer_tip_radius
            otip_by = center + math.sin(angle_b) * outer_tip_radius

            pygame.draw.line(surf, (255, 127, 39), (opx, opy), (otip_ax, otip_ay), 3)
            pygame.draw.line(surf, (255, 127, 39), (opx, opy), (otip_bx, otip_by), 3)
            pygame.draw.circle(surf, (255, 127, 39), (int(opx), int(opy)), 3)

        triangle_size = 25
        triangle_points = []
        for i in range(3):
            angle = math.radians(120 * i - 90)
            tx = center + math.cos(angle) * triangle_size
            ty = center + math.sin(angle) * triangle_size
            triangle_points.append((tx, ty))
        pygame.draw.polygon(surf, (200, 100, 0), triangle_points)
        pygame.draw.polygon(surf, (255, 150, 0), triangle_points, 2)

        pygame.draw.circle(surf, (255, 50, 0), (center, center), 15)
        pygame.draw.circle(surf, (255, 255, 0), (center, center), 10)
        pygame.draw.circle(surf, WHITE, (center, center), 5)

        return surf

    def create_damaged_sprite(self):
        """Cree un sprite endommage"""
        surf = self.create_sprite()
        flash = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 150))
        surf.blit(flash, (0, 0))
        return surf

    def create_shield_sprite(self):
        """Cree un sprite avec bouclier"""
        surf = self.create_sprite()
        shield_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (255, 215, 0, 100), (self.size // 2, self.size // 2), 75)
        pygame.draw.circle(shield_surf, (255, 255, 200, 200), (self.size // 2, self.size // 2), 75, 3)
        surf.blit(shield_surf, (0, 0))
        return surf

    def draw_aura(self, surface, cx, cy, pulse):
        """Dessine l'aura pulsante autour du boss"""
        aura_size = int(90 * pulse)
        aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (255, 200, 0, 30), (aura_size, aura_size), aura_size)
        surface.blit(aura_surf, (cx - aura_size, cy - aura_size))

    def draw_rings(self, surface, cx, cy, ring_rotation):
        """Dessine les anneaux orbitaux rotatifs"""
        for i in range(3):
            ring_radius = 85 + i * 15
            ring_alpha = 100 - i * 30
            ring_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 215, 0, ring_alpha),
                             (ring_radius + 5, ring_radius + 5), ring_radius, 2)
            rotated = pygame.transform.rotate(ring_surf, ring_rotation * (i + 1) * 0.5)
            rot_rect = rotated.get_rect(center=(cx, cy))
            surface.blit(rotated, rot_rect)

    def draw_orbs(self, surface, cx, cy, ring_rotation):
        """Dessine les orbes orbitales"""
        for i in range(6):
            angle = math.radians(ring_rotation * 2 + i * 60)
            orb_x = cx + math.cos(angle) * 80
            orb_y = cy + math.sin(angle) * 50
            pygame.draw.circle(surface, (255, 200, 0), (int(orb_x), int(orb_y)), 6)
            pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), 3)

    def draw_swoop_warning(self, surface, cx, cy, charge_timer, charge_warning_duration, swoop_phase, target_y):
        """Dessine le warning visuel du swoop (trajectoire + flash)"""
        warning_alpha = int(200 * abs(math.sin(charge_timer * 0.4)))

        # Trace de la trajectoire elliptique en pointilles
        trajectory_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ellipse_cx = SCREEN_WIDTH // 2
        ellipse_cy = target_y + 380
        radius_x = 300
        radius_y = 380
        num_points = 60
        progress = charge_timer / charge_warning_duration if swoop_phase == 0 else 1.0
        visible_points = int(num_points * min(1.0, progress * 1.5))
        for i in range(visible_points):
            t = i / num_points
            angle = math.pi / 2 - t * 2 * math.pi
            px = ellipse_cx - int(math.cos(angle) * radius_x)
            py = ellipse_cy - int(math.sin(angle) * radius_y)
            if i % 2 == 0:
                dot_alpha = int(warning_alpha * (0.4 + 0.6 * (1 - t)))
                pygame.draw.circle(trajectory_surf, (255, 180, 50, dot_alpha), (px, py), 3)

        # Fleche directionnelle animee
        arrow_t = (charge_timer * 0.02) % 1.0
        arrow_angle = math.pi / 2 - arrow_t * 2 * math.pi
        arrow_x = ellipse_cx - int(math.cos(arrow_angle) * radius_x)
        arrow_y = ellipse_cy - int(math.sin(arrow_angle) * radius_y)
        pygame.draw.circle(trajectory_surf, (255, 255, 150, warning_alpha), (arrow_x, arrow_y), 6)
        pygame.draw.circle(trajectory_surf, (255, 255, 255, warning_alpha), (arrow_x, arrow_y), 3)

        surface.blit(trajectory_surf, (0, 0))

        # Flash au centre du boss
        flash_r = int(60 + math.sin(charge_timer * 0.6) * 20)
        flash_surf = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 255, 200, int(warning_alpha * 0.5)),
                         (flash_r, flash_r), flash_r)
        surface.blit(flash_surf, (cx - flash_r, cy - flash_r))
