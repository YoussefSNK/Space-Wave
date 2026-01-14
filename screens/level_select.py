import pygame
from screens.base import Screen, Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE
from graphics.background import Background


class LevelButton(Button):
    """Bouton spécial pour la sélection de niveau."""

    def __init__(self, x, y, level_num, locked=False):
        width = 150
        height = 150
        super().__init__(x, y, width, height, "", font_size=48)
        self.level_num = level_num
        self.locked = locked

        if locked:
            self.color_normal = (30, 30, 40)
            self.color_hover = (30, 30, 40)
            self.color_border = (60, 60, 70)
        else:
            self.color_normal = (40, 60, 100)
            self.color_hover = (60, 90, 140)
            self.color_border = (80, 120, 180)

    def handle_event(self, event):
        if self.locked:
            return False
        return super().handle_event(event)

    def draw(self, surface):
        color = self.color_hover if (self.hovered and not self.locked) else self.color_normal
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, self.color_border, self.rect, width=3, border_radius=12)

        font = pygame.font.SysFont(None, self.font_size)

        if self.locked:
            # Afficher un cadenas
            lock_text = font.render("🔒", True, (80, 80, 80))
            lock_rect = lock_text.get_rect(center=self.rect.center)
            surface.blit(lock_text, lock_rect)
        else:
            # Numéro du niveau
            level_text = font.render(str(self.level_num), True, self.color_text)
            level_rect = level_text.get_rect(center=(self.rect.centerx, self.rect.centery - 15))
            surface.blit(level_text, level_rect)

            # Sous-titre "Niveau"
            small_font = pygame.font.SysFont(None, 24)
            subtitle = small_font.render("Niveau", True, (180, 180, 200))
            subtitle_rect = subtitle.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
            surface.blit(subtitle, subtitle_rect)


class LevelSelectScreen(Screen):
    """Écran de sélection de niveau."""

    def __init__(self, screen, scalable_display=None):
        super().__init__(screen, scalable_display)
        self.background = Background()
        self.selected_level = None

        # Configuration des niveaux (pour l'instant, un seul débloqué)
        # Structure prête pour le multijoueur : on pourra ajouter des niveaux facilement
        self.levels = [
            {"num": 1, "locked": False, "name": "Première vague"},
            {"num": 2, "locked": True, "name": "À venir..."},
            {"num": 3, "locked": True, "name": "À venir..."},
        ]

        # Créer les boutons de niveau
        self.level_buttons = []
        start_x = (SCREEN_WIDTH - (len(self.levels) * 170 - 20)) // 2
        y = SCREEN_HEIGHT // 2 - 50

        for i, level in enumerate(self.levels):
            x = start_x + i * 170
            button = LevelButton(x, y, level["num"], locked=level["locked"])
            self.level_buttons.append(button)

        # Bouton retour
        self.back_button = Button(
            50, SCREEN_HEIGHT - 80, 150, 45, "← Retour", font_size=32
        )

        # Bouton multijoueur
        self.multiplayer_button = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 800, 200, 45, "Multijoueur", font_size=32
        )
        self.multiplayer_button.color_normal = (60, 40, 100)
        self.multiplayer_button.color_hover = (90, 60, 140)
        self.multiplayer_button.color_border = (120, 80, 180)

    def handle_event(self, event):
        for i, button in enumerate(self.level_buttons):
            if button.handle_event(event):
                self.selected_level = self.levels[i]["num"]
                self.next_screen = "game"
                self.running = False

        if self.back_button.handle_event(event):
            self.next_screen = "menu"
            self.running = False

        if self.multiplayer_button.handle_event(event):
            self.next_screen = "lobby"
            self.running = False

    def update(self):
        self.background.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        # Titre
        title_font = pygame.font.SysFont(None, 56)
        title_text = title_font.render("Sélection du niveau", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.SysFont(None, 28)
        subtitle_text = subtitle_font.render("Choisissez votre destination", True, (150, 150, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 165))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Boutons de niveau
        for button in self.level_buttons:
            button.draw(self.screen)

        # Noms des niveaux en dessous des boutons
        name_font = pygame.font.SysFont(None, 22)
        for i, button in enumerate(self.level_buttons):
            name = self.levels[i]["name"]
            color = (100, 100, 100) if self.levels[i]["locked"] else (180, 180, 200)
            name_text = name_font.render(name, True, color)
            name_rect = name_text.get_rect(center=(button.rect.centerx, button.rect.bottom + 20))
            self.screen.blit(name_text, name_rect)

        # Bouton retour
        self.back_button.draw(self.screen)

        # Bouton multijoueur
        self.multiplayer_button.draw(self.screen)

    def get_selected_level(self):
        """Retourne le niveau sélectionné."""
        return self.selected_level
