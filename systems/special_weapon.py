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
}


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

    def update(self):
        """Met a jour les timers d'animation."""
        if self.trigger_animation_timer > 0:
            self.trigger_animation_timer -= 1

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
