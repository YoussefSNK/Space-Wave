import pygame
from screens.base import Screen, Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE
from graphics.shared_background import get_shared_background, set_background_speed


class MenuScreen(Screen):
    """Écran d'accueil / menu principal."""

    def __init__(self, screen, scalable_display=None):
        super().__init__(screen, scalable_display)
        self.background = get_shared_background()
        set_background_speed(2)  # Vitesse standard pour le menu

        # Titre du jeu
        self.title_font = pygame.font.SysFont(None, 72)
        self.subtitle_font = pygame.font.SysFont(None, 36)

        # Boutons centrés
        button_width = 250
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        start_y = SCREEN_HEIGHT // 2

        self.play_button = Button(
            button_x, start_y, button_width, button_height, "Jouer", font_size=40
        )
        self.quit_button = Button(
            button_x, start_y + 80, button_width, button_height, "Quitter", font_size=40
        )

        # Animation du titre
        self.title_offset = 0
        self.title_direction = 1

    def handle_event(self, event):
        if self.play_button.handle_event(event):
            self.next_screen = "level_select"
            self.running = False

        if self.quit_button.handle_event(event):
            self.next_screen = None
            self.running = False

    def update(self):
        self.background.update()

        # Animation légère du titre
        self.title_offset += 0.1 * self.title_direction
        if abs(self.title_offset) > 5:
            self.title_direction *= -1

    def draw(self):
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        # Titre avec effet de flottement
        title_text = self.title_font.render("SPACE WAVE", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200 + self.title_offset))
        self.screen.blit(title_text, title_rect)

        # Sous-titre
        subtitle_text = self.subtitle_font.render("Un shoot'em up spatial", True, (150, 150, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Boutons
        self.play_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        # Instructions en bas
        hint_font = pygame.font.SysFont(None, 24)
        hint_text = hint_font.render("Utilisez la souris pour vous déplacer et tirer", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_text, hint_rect)
