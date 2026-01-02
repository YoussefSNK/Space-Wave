import pygame
from abc import ABC, abstractmethod


class Screen(ABC):
    """Classe de base pour tous les écrans du jeu."""

    def __init__(self, screen):
        self.screen = screen
        self.next_screen = None
        self.running = True

    @abstractmethod
    def handle_event(self, event):
        """Gère les événements pygame."""
        pass

    @abstractmethod
    def update(self):
        """Met à jour la logique de l'écran."""
        pass

    @abstractmethod
    def draw(self):
        """Dessine l'écran."""
        pass

    def run(self):
        """Boucle principale de l'écran. Retourne le prochain écran ou None pour quitter."""
        clock = pygame.time.Clock()
        from config import FPS

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                self.handle_event(event)

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        return self.next_screen


class Button:
    """Bouton cliquable pour les menus."""

    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.hovered = False
        self.color_normal = (50, 50, 80)
        self.color_hover = (80, 80, 120)
        self.color_border = (100, 100, 150)
        self.color_text = (255, 255, 255)

    def handle_event(self, event):
        """Retourne True si le bouton est cliqué."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        color = self.color_hover if self.hovered else self.color_normal
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color_border, self.rect, width=2, border_radius=8)

        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, self.color_text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
