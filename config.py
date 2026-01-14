import pygame

# Dimensions internes du jeu (résolution de référence)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 1000
FPS = 60

# Taille minimale de la fenêtre
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500

# Classe pour gérer le scaling de la fenêtre
class ScalableDisplay:
    def __init__(self, window_width=None, window_height=None):
        # Surface interne où le jeu est dessiné (résolution fixe)
        self.internal_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Taille initiale de la fenêtre (peut être plus petite que la résolution interne)
        self.window_width = window_width or SCREEN_WIDTH
        self.window_height = window_height or SCREEN_HEIGHT

        # Créer la fenêtre redimensionnable
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )

        # Calculer le scaling initial
        self._update_scaling()

    def _update_scaling(self):
        """Calcule le facteur de scale et la position pour centrer le jeu."""
        # Calculer le ratio pour garder les proportions
        ratio_w = self.window_width / SCREEN_WIDTH
        ratio_h = self.window_height / SCREEN_HEIGHT
        self.scale = min(ratio_w, ratio_h)

        # Taille du jeu mis à l'échelle
        self.scaled_width = int(SCREEN_WIDTH * self.scale)
        self.scaled_height = int(SCREEN_HEIGHT * self.scale)

        # Position pour centrer (barres noires si nécessaire)
        self.offset_x = (self.window_width - self.scaled_width) // 2
        self.offset_y = (self.window_height - self.scaled_height) // 2

    def handle_resize(self, new_width, new_height):
        """Gère le redimensionnement de la fenêtre."""
        # Appliquer les tailles minimales
        self.window_width = max(new_width, MIN_WINDOW_WIDTH)
        self.window_height = max(new_height, MIN_WINDOW_HEIGHT)

        # Recréer la fenêtre avec la nouvelle taille
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )

        self._update_scaling()

    def get_internal_surface(self):
        """Retourne la surface interne où dessiner le jeu."""
        return self.internal_surface

    def render(self):
        """Met à l'échelle et affiche le jeu dans la fenêtre."""
        # Effacer la fenêtre (barres noires)
        self.window.fill((0, 0, 0))

        # Mettre à l'échelle la surface interne
        scaled_surface = pygame.transform.scale(
            self.internal_surface,
            (self.scaled_width, self.scaled_height)
        )

        # Dessiner au centre de la fenêtre
        self.window.blit(scaled_surface, (self.offset_x, self.offset_y))

        pygame.display.flip()

    def screen_to_game_coords(self, screen_x, screen_y):
        """Convertit les coordonnées de la fenêtre en coordonnées du jeu."""
        game_x = (screen_x - self.offset_x) / self.scale
        game_y = (screen_y - self.offset_y) / self.scale
        return game_x, game_y

# Couleurs
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
