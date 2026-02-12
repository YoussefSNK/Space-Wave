import pygame
import random

from config import SCREEN_WIDTH, WHITE


SPECIAL_WEAPONS = {
    "la_vague": {
        "name": "La Vague",
        "milestone": 10,
        "color": (0, 150, 255),
    },
    "pardon": {
        "name": "Pardon",
        "milestone": 15,
        "color": (0, 255, 100),
    },
    "laser": {
        "name": "Laser",
        "milestone": 12,
        "color": (255, 50, 50),
    },
}


class LaserBeam:
    """Rayon laser qui suit le vaisseau et dure 1 seconde."""

    def __init__(self, player):
        self.player = player
        self.duration = 60  # 1 seconde a 60 FPS
        self.timer = self.duration
        self.width = player.rect.width * 2  # 2 fois la largeur du vaisseau
        self.color = (255, 50, 50)
        self.active = True
        self.damage_cooldown = 10  # Frames entre chaque degat
        self.hit_enemies = {}  # enemy_id -> frames restantes avant prochain degat

    def update(self):
        """Met a jour le timer du laser."""
        if self.timer > 0:
            self.timer -= 1
        else:
            self.active = False

        # Reduire les cooldowns des ennemis touches
        for enemy_id in list(self.hit_enemies.keys()):
            self.hit_enemies[enemy_id] -= 1
            if self.hit_enemies[enemy_id] <= 0:
                del self.hit_enemies[enemy_id]

    def get_rect(self):
        """Retourne le rectangle de collision du laser."""
        x = self.player.rect.centerx - self.width // 2
        y = 0
        height = self.player.rect.top
        return pygame.Rect(x, y, self.width, height)

    def check_collision(self, enemy):
        """Verifie si le laser touche un ennemi et peut lui infliger des degats."""
        if not self.active:
            return False

        # Verifier si l'ennemi est en collision
        if not self.get_rect().colliderect(enemy.rect):
            return False

        # Verifier le cooldown pour cet ennemi
        enemy_id = id(enemy)
        if enemy_id in self.hit_enemies:
            return False

        # Marquer l'ennemi comme touche avec cooldown
        self.hit_enemies[enemy_id] = self.damage_cooldown
        return True

    def draw(self, surface):
        """Dessine le rayon laser."""
        if not self.active:
            return

        # Position du laser (du haut de l'ecran jusqu'au vaisseau)
        x = self.player.rect.centerx - self.width // 2
        y = 0
        height = self.player.rect.top

        # Effet de pulsation base sur le timer
        progress = self.timer / self.duration
        pulse = 0.8 + 0.2 * abs((self.timer % 10) - 5) / 5

        # Couleur avec intensite variable
        intensity = int(255 * progress * pulse)
        core_color = (255, intensity, intensity)

        # Dessiner le coeur du laser (plus lumineux)
        core_width = int(self.width * 0.6)
        core_x = self.player.rect.centerx - core_width // 2
        core_surf = pygame.Surface((core_width, height), pygame.SRCALPHA)
        core_surf.fill((*core_color, int(200 * progress)))
        surface.blit(core_surf, (core_x, y))

        # Dessiner le halo externe (plus transparent)
        halo_surf = pygame.Surface((self.width, height), pygame.SRCALPHA)
        halo_surf.fill((255, 100, 100, int(100 * progress)))
        surface.blit(halo_surf, (x, y))

        # Effet de bord brillant
        edge_color = (255, 255, 255, int(150 * progress * pulse))
        edge_surf = pygame.Surface((4, height), pygame.SRCALPHA)
        edge_surf.fill(edge_color)
        surface.blit(edge_surf, (x, y))
        surface.blit(edge_surf, (x + self.width - 4, y))


class SpecialWeapon:
    """Arme speciale permanente assignee au joueur pour toute la partie.
    Se declenche quand le combo atteint un multiple du milestone."""

    def __init__(self, weapon_type=None):
        if weapon_type is None:
            weapon_type = random.choice(list(SPECIAL_WEAPONS.keys()))
        self.weapon_type = weapon_type
        self.config = SPECIAL_WEAPONS[weapon_type]
        self.milestone = self.config["milestone"]
        self.last_triggered_at = 0
        self.trigger_animation_timer = 0
        self.trigger_animation_duration = 60
        self.active_laser = None  # Laser actif (si applicable)

    def check_trigger(self, combo_count):
        """Verifie si le combo a atteint un nouveau palier."""
        if combo_count <= 0:
            self.last_triggered_at = 0
            return False
        if combo_count % self.milestone != 0:
            return False
        if combo_count == self.last_triggered_at:
            return False
        self.last_triggered_at = combo_count
        self.trigger_animation_timer = self.trigger_animation_duration
        return True

    def activate(self, player, projectile_list):
        """Execute l'effet de l'arme speciale."""
        if self.weapon_type == "la_vague":
            self._fire_la_vague(player, projectile_list)
        elif self.weapon_type == "pardon":
            self._heal_pardon(player)
        elif self.weapon_type == "laser":
            self._fire_laser(player)

    def _fire_la_vague(self, player, projectile_list):
        """Tire 10 projectiles paralleles repartis sur la largeur de l'ecran."""
        from entities.projectiles import Projectile

        num_shots = 10
        margin = 40
        spacing = (SCREEN_WIDTH - 2 * margin) / (num_shots - 1)
        y = player.rect.top

        for i in range(num_shots):
            x = margin + i * spacing
            proj = Projectile(int(x), y, speed=12)
            proj.is_special_weapon = True
            proj.image.fill((0, 150, 255))
            projectile_list.append(proj)

    def _heal_pardon(self, player):
        """Soigne le joueur de 1 HP."""
        player.hp += 1

    def _fire_laser(self, player):
        """Active un rayon laser qui suit le vaisseau."""
        self.active_laser = LaserBeam(player)

    def update(self):
        """Met a jour les timers d'animation."""
        if self.trigger_animation_timer > 0:
            self.trigger_animation_timer -= 1

        # Mettre a jour le laser actif
        if self.active_laser:
            self.active_laser.update()
            if not self.active_laser.active:
                self.active_laser = None

    def check_laser_collision(self, enemy):
        """Verifie si le laser actif touche un ennemi."""
        if self.active_laser:
            return self.active_laser.check_collision(enemy)
        return False

    def draw(self, surface, font):
        """Affiche l'indicateur de l'arme speciale."""
        color = self.config["color"]
        name = self.config["name"]
        milestone = self.milestone

        text = font.render(f"[{name}] x{milestone}", True, color)
        text_rect = text.get_rect()
        text_rect.topright = (SCREEN_WIDTH - 10, 40)
        surface.blit(text, text_rect)

        if self.trigger_animation_timer > 0:
            progress = self.trigger_animation_timer / self.trigger_animation_duration
            alpha = int(200 * progress)
            trigger_text = font.render(f"{name} !", True, WHITE)
            trigger_rect = trigger_text.get_rect()
            trigger_rect.center = (SCREEN_WIDTH // 2, 80)

            flash_surf = pygame.Surface(trigger_text.get_size(), pygame.SRCALPHA)
            flash_surf.blit(trigger_text, (0, 0))
            flash_surf.set_alpha(alpha)
            surface.blit(flash_surf, trigger_rect)

        # Dessiner le laser actif
        if self.active_laser:
            self.active_laser.draw(surface)
