import pygame
from config import ScalableDisplay
from screens.menu import MenuScreen
from screens.level_select import LevelSelectScreen
from screens.game_screen import GameScreen
from screens.lobby import LobbyScreen
from screens.multiplayer_game import MultiplayerGameScreen


def main():
    pygame.init()

    # Créer le système d'affichage redimensionnable
    display = ScalableDisplay()
    pygame.display.set_caption("Space Wave")

    # La surface interne où le jeu est dessiné (toujours 800x1000)
    screen = display.get_internal_surface()

    current_screen = "menu"
    selected_level = 1
    network_client = None

    while current_screen is not None:
        if current_screen == "menu":
            menu = MenuScreen(screen, display)
            current_screen = menu.run()

        elif current_screen == "level_select":
            level_select = LevelSelectScreen(screen, display)
            current_screen = level_select.run()
            if current_screen == "game":
                selected_level = level_select.get_selected_level()

        elif current_screen == "game":
            game = GameScreen(screen, display, level_num=selected_level)
            current_screen = game.run()

        elif current_screen == "lobby":
            lobby = LobbyScreen(screen, display)
            current_screen = lobby.run()
            if current_screen == "multiplayer_game":
                network_client = lobby.get_client()

        elif current_screen == "multiplayer_game":
            if network_client:
                mp_game = MultiplayerGameScreen(screen, display, network_client)
                current_screen = mp_game.run()
                network_client.disconnect()
                network_client = None
            else:
                current_screen = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()
