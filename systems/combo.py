import pygame

from config import SCREEN_WIDTH, YELLOW


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
