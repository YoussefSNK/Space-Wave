"""
Zone de test pour prévisualiser les différents backgrounds du jeu.
Permet de naviguer entre les backgrounds, ajuster la vitesse de défilement,
et observer le rendu en temps réel.
"""

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, YELLOW
from graphics.background import Background, SpiralNebulaBackground, AuroraBackground, GalaxyBackground, CosmicVortexBackground, BacklitFractalBackground


def show_menu(screen, font):
    """Affiche le menu de sélection des backgrounds."""
    options = [
        "1 - Nébuleuse Perlin (actuel)",
        "2 - Nébuleuse spirale",
        "3 - Aurore cosmique",
        "4 - Galaxie 3D",
        "5 - Vortex cosmique",
        "6 - Fractale rétro-éclairée",
        "",
        "ESC - Quitter"
    ]

    screen.fill(BLACK)
    title = font.render("TEST DES BACKGROUNDS", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

    subtitle = font.render("Choisissez un background:", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 300))

    colors = [
        (100, 150, 255),   # Bleu pour Perlin
        (180, 100, 255),   # Violet pour spirale
        (100, 255, 150),   # Vert pour aurore
        (255, 150, 80),    # Orange pour galaxie
        (255, 80, 80),     # Rouge pour vortex
        (200, 100, 255),   # Violet pour fractale
    ]

    for i, option in enumerate(options):
        if not option:
            continue
        if i < len(colors):
            color = colors[i]
        else:
            color = WHITE
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 400 + i * 60))

    pygame.display.flip()


def run_background_test(bg_type):
    """Lance le test d'un background spécifique."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Test - {bg_type}")
    clock = pygame.time.Clock()

    # Créer le background
    if bg_type == "Nébuleuse Perlin":
        background = Background(speed=2)
    elif bg_type == "Nébuleuse spirale":
        background = SpiralNebulaBackground(speed=2)
    elif bg_type == "Aurore cosmique":
        background = AuroraBackground(speed=2)
    elif bg_type == "Galaxie 3D":
        background = GalaxyBackground(speed=2)
    elif bg_type == "Vortex cosmique":
        background = CosmicVortexBackground(speed=2)
    elif bg_type == "Fractale rétro-éclairée":
        background = BacklitFractalBackground(speed=2)

    speed = 2.0
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key == pygame.K_UP:
                    speed = min(speed + 0.5, 10.0)
                    background.speed = speed
                if event.key == pygame.K_DOWN:
                    speed = max(speed - 0.5, 0.0)
                    background.speed = speed
                if event.key == pygame.K_SPACE:
                    # Pause / reprise
                    if background.speed > 0:
                        background.speed = 0
                    else:
                        background.speed = speed

        background.update()

        # Rendu
        screen.fill(BLACK)
        background.draw(screen)

        # UI
        title_text = font.render(f"Background: {bg_type}", True, YELLOW)
        screen.blit(title_text, (10, 10))

        speed_text = font.render(f"Vitesse: {background.speed:.1f}", True, WHITE)
        screen.blit(speed_text, (10, 50))

        # Instructions
        instructions = [
            "HAUT/BAS: Ajuster la vitesse",
            "ESPACE: Pause/Reprise",
            "ESC: Retour au menu"
        ]
        for i, instr in enumerate(instructions):
            text = small_font.render(instr, True, (150, 150, 150))
            screen.blit(text, (10, SCREEN_HEIGHT - 90 + i * 25))

        pygame.display.flip()
        clock.tick(FPS)

    return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test des Backgrounds - Menu")
    font = pygame.font.SysFont(None, 48)

    running = True
    while running:
        show_menu(screen, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    if not run_background_test("Nébuleuse Perlin"):
                        running = False
                elif event.key == pygame.K_2:
                    if not run_background_test("Nébuleuse spirale"):
                        running = False
                elif event.key == pygame.K_3:
                    if not run_background_test("Aurore cosmique"):
                        running = False
                elif event.key == pygame.K_4:
                    if not run_background_test("Galaxie 3D"):
                        running = False
                elif event.key == pygame.K_5:
                    if not run_background_test("Vortex cosmique"):
                        running = False
                elif event.key == pygame.K_6:
                    if not run_background_test("Fractale rétro-éclairée"):
                        running = False

    pygame.quit()


if __name__ == "__main__":
    main()
