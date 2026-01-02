import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from screens.menu import MenuScreen
from screens.level_select import LevelSelectScreen
from screens.game_screen import GameScreen


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Wave")

    current_screen = "menu"
    selected_level = 1

    while current_screen is not None:
        if current_screen == "menu":
            menu = MenuScreen(screen)
            current_screen = menu.run()

        elif current_screen == "level_select":
            level_select = LevelSelectScreen(screen)
            current_screen = level_select.run()
            if current_screen == "game":
                selected_level = level_select.get_selected_level()

        elif current_screen == "game":
            game = GameScreen(screen, level_num=selected_level)
            current_screen = game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
