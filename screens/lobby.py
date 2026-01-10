"""Écran de lobby pour le multijoueur avec serveur central."""

import pygame
import threading
from screens.base import Screen, Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, CYAN
from graphics.background import Background
from network.client import GameClient


class TextInput:
    """Champ de saisie de texte."""

    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.font.SysFont(None, 32)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.unicode.isprintable() and len(self.text) < 30:
                self.text += event.unicode
        return False

    def draw(self, surface):
        color = (60, 60, 80) if self.active else (40, 40, 60)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (100, 100, 120), self.rect, width=2, border_radius=5)

        display_text = self.text if self.text else self.placeholder
        text_color = WHITE if self.text else (100, 100, 120)
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)


class LobbyListItem:
    """Un élément de la liste des lobbies."""

    def __init__(self, x, y, width, height, lobby_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.lobby_data = lobby_data
        self.hovered = False
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            return True
        return False

    def draw(self, surface):
        color = (60, 80, 100) if self.hovered else (40, 50, 70)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (80, 100, 130), self.rect, width=2, border_radius=5)

        # Nom du lobby
        name = self.lobby_data.get("name", "Sans nom")
        name_text = self.font.render(name, True, WHITE)
        surface.blit(name_text, (self.rect.x + 15, self.rect.y + 10))

        # Hôte
        host = self.lobby_data.get("host_name", "???")
        host_text = self.small_font.render(f"Hôte: {host}", True, (150, 150, 180))
        surface.blit(host_text, (self.rect.x + 15, self.rect.y + 38))

        # Joueurs
        count = self.lobby_data.get("player_count", 0)
        max_p = self.lobby_data.get("max_players", 2)
        count_text = self.small_font.render(f"{count}/{max_p}", True, CYAN)
        count_rect = count_text.get_rect(midright=(self.rect.right - 15, self.rect.centery))
        surface.blit(count_text, count_rect)


class LobbyScreen(Screen):
    """Écran de lobby pour rejoindre ou créer une partie."""

    def __init__(self, screen):
        super().__init__(screen)
        self.background = Background()
        self.client: GameClient = None

        # États: "connecting", "browse", "create", "in_lobby"
        self.state = "connecting"
        self.error_message = ""
        self.refresh_timer = 0

        # Liste des lobbies
        self.lobby_items = []
        self.scroll_offset = 0

        # Champs de saisie
        center_x = SCREEN_WIDTH // 2
        self.name_input = TextInput(
            center_x - 150, 180, 300, 40, "Votre pseudo"
        )
        self.name_input.text = "Joueur"

        self.lobby_name_input = TextInput(
            center_x - 150, 280, 300, 40, "Nom du lobby"
        )

        self.ip_input = TextInput(
            center_x - 150, 180, 300, 40, "IP du serveur (optionnel)"
        )

        # Boutons - Connexion
        self.connect_button = Button(
            center_x - 100, 250, 200, 45, "Se connecter", font_size=32
        )

        # Boutons - Navigation
        self.create_lobby_btn = Button(
            center_x - 150, 130, 300, 45, "Créer un lobby", font_size=32
        )
        self.refresh_btn = Button(
            center_x + 170, 130, 120, 45, "Actualiser", font_size=24
        )
        self.back_button = Button(
            50, SCREEN_HEIGHT - 80, 150, 45, "← Retour", font_size=32
        )

        # Boutons - Création de lobby
        self.confirm_create_btn = Button(
            center_x - 100, 370, 200, 45, "Créer", font_size=32
        )
        self.confirm_create_btn.color_normal = (40, 100, 40)
        self.confirm_create_btn.color_hover = (60, 140, 60)

        self.cancel_btn = Button(
            center_x - 100, 430, 200, 45, "Annuler", font_size=32
        )

        # Boutons - Dans le lobby
        self.ready_button = Button(
            center_x - 100, SCREEN_HEIGHT - 150, 200, 50, "Prêt !", font_size=36
        )
        self.ready_button.color_normal = (40, 100, 40)
        self.ready_button.color_hover = (60, 140, 60)

        self.leave_lobby_btn = Button(
            center_x - 100, SCREEN_HEIGHT - 80, 200, 45, "Quitter le lobby", font_size=28
        )

        self.is_ready = False

        # Démarrer la connexion
        self._start_connection()

    def _start_connection(self):
        """Démarre la connexion au serveur."""
        self.state = "connecting"
        self.error_message = ""

        def connect():
            self.client = GameClient()
            ip = self.ip_input.text.strip()

            if ip:
                servers = [ip]
            else:
                servers = ["space-wave.onrender.com", "localhost"]

            for server in servers:
                print(f"Tentative de connexion à {server}...")
                if self.client.connect(server, 5555):
                    print(f"Connecté à {server}")
                    self.state = "browse"
                    self.client.request_lobby_list()
                    return
                print(f"Échec de connexion à {server}")

            self.error_message = "Impossible de se connecter aux serveurs"
            self.state = "disconnected"

        thread = threading.Thread(target=connect, daemon=True)
        thread.start()

    def handle_event(self, event):
        if self.state == "disconnected":
            self.ip_input.handle_event(event)
            if self.connect_button.handle_event(event):
                self._start_connection()

        elif self.state == "browse":
            self.name_input.handle_event(event)

            if self.create_lobby_btn.handle_event(event):
                self.state = "create"
                self.lobby_name_input.text = f"Partie de {self.name_input.text.strip() or 'Joueur'}"

            if self.refresh_btn.handle_event(event):
                if self.client:
                    self.client.request_lobby_list()

            # Clic sur un lobby
            for item in self.lobby_items:
                if item.handle_event(event):
                    self._join_lobby(item.lobby_data.get("lobby_id"))

            # Scroll
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset = max(0, self.scroll_offset - event.y * 30)

        elif self.state == "create":
            self.name_input.handle_event(event)
            self.lobby_name_input.handle_event(event)

            if self.confirm_create_btn.handle_event(event):
                self._create_lobby()

            if self.cancel_btn.handle_event(event):
                self.state = "browse"

        elif self.state == "in_lobby":
            if self.ready_button.handle_event(event) and not self.is_ready:
                self.is_ready = True
                if self.client:
                    self.client.send_ready()

            if self.leave_lobby_btn.handle_event(event):
                if self.client:
                    self.client.leave_lobby()
                self.state = "browse"
                self.is_ready = False
                self.client.request_lobby_list()

        if self.back_button.handle_event(event):
            self._cleanup()
            self.next_screen = "level_select"
            self.running = False

    def _create_lobby(self):
        """Crée un nouveau lobby."""
        if self.client and self.client.connected:
            player_name = self.name_input.text.strip() or "Joueur"
            lobby_name = self.lobby_name_input.text.strip() or f"Partie de {player_name}"
            self.client.create_lobby(player_name, lobby_name)
            self.state = "in_lobby"
            self.is_ready = False

    def _join_lobby(self, lobby_id: str):
        """Rejoint un lobby existant."""
        if self.client and self.client.connected:
            player_name = self.name_input.text.strip() or "Joueur"
            self.client.join_lobby(player_name, lobby_id)
            self.state = "in_lobby"
            self.is_ready = False

    def _cleanup(self):
        """Nettoie les ressources."""
        if self.client:
            self.client.disconnect()
            self.client = None

    def update(self):
        self.background.update()

        # Vérifier si la partie commence
        if self.client and self.client.game_started:
            self.next_screen = "multiplayer_game"
            self.running = False
            return

        # Mettre à jour la liste des lobbies
        if self.client and self.client.lobbies_updated:
            self.client.lobbies_updated = False
            self._rebuild_lobby_list()

        # Rafraîchir périodiquement
        if self.state == "browse":
            self.refresh_timer += 1
            if self.refresh_timer >= 180:  # Toutes les 3 secondes
                self.refresh_timer = 0
                if self.client and self.client.connected:
                    self.client.request_lobby_list()

        # Vérifier les erreurs de lobby
        if self.client and self.client.lobby_error:
            self.error_message = self.client.lobby_error
            self.client.lobby_error = None
            self.state = "browse"

        # Vérifier si on est entré dans un lobby
        if self.state == "in_lobby" and self.client and not self.client.in_lobby():
            # On attend la confirmation
            pass

    def _rebuild_lobby_list(self):
        """Reconstruit la liste visuelle des lobbies."""
        self.lobby_items = []
        y = 200
        for lobby_data in self.client.lobbies:
            item = LobbyListItem(
                SCREEN_WIDTH // 2 - 200, y - self.scroll_offset,
                400, 70, lobby_data
            )
            self.lobby_items.append(item)
            y += 80

    def draw(self):
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        # Titre
        title_font = pygame.font.SysFont(None, 56)
        title_text = title_font.render("Multijoueur", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)

        if self.state == "connecting":
            self._draw_connecting()
        elif self.state == "disconnected":
            self._draw_disconnected()
        elif self.state == "browse":
            self._draw_browse()
        elif self.state == "create":
            self._draw_create()
        elif self.state == "in_lobby":
            self._draw_in_lobby()

        # Bouton retour toujours visible
        self.back_button.draw(self.screen)

        # Message d'erreur
        if self.error_message:
            error_font = pygame.font.SysFont(None, 28)
            error_text = error_font.render(self.error_message, True, (255, 100, 100))
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(error_text, error_rect)

    def _draw_connecting(self):
        """Dessine l'écran de connexion."""
        font = pygame.font.SysFont(None, 36)
        text = font.render("Connexion au serveur...", True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw_disconnected(self):
        """Dessine l'écran de déconnexion."""
        font = pygame.font.SysFont(None, 32)
        label_font = pygame.font.SysFont(None, 28)

        # Message
        msg = font.render("Connexion au serveur", True, WHITE)
        self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        # Champ IP
        ip_label = label_font.render("Adresse du serveur :", True, (180, 180, 200))
        self.screen.blit(ip_label, (SCREEN_WIDTH // 2 - 150, 150))
        self.ip_input.draw(self.screen)

        self.connect_button.draw(self.screen)

        # Instructions
        hint_font = pygame.font.SysFont(None, 22)
        hint = hint_font.render("Assurez-vous que le serveur est lancé (python -m network.server)", True, (100, 100, 130))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 320)))

    def _draw_browse(self):
        """Dessine l'écran de navigation des lobbies."""
        font = pygame.font.SysFont(None, 28)

        # Pseudo
        name_label = font.render("Pseudo :", True, (180, 180, 200))
        self.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, 90))
        self.name_input.rect.y = 85
        self.name_input.rect.x = SCREEN_WIDTH // 2 - 20
        self.name_input.rect.width = 170
        self.name_input.draw(self.screen)

        # Boutons
        self.create_lobby_btn.draw(self.screen)
        self.refresh_btn.draw(self.screen)

        # Liste des lobbies
        subtitle = font.render("Lobbies disponibles :", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - 200, 190))

        if not self.lobby_items:
            empty_text = font.render("Aucun lobby disponible", True, (100, 100, 130))
            self.screen.blit(empty_text, empty_text.get_rect(center=(SCREEN_WIDTH // 2, 300)))
            hint_text = pygame.font.SysFont(None, 24).render(
                "Créez un lobby et attendez qu'un autre joueur vous rejoigne",
                True, (80, 80, 100)
            )
            self.screen.blit(hint_text, hint_text.get_rect(center=(SCREEN_WIDTH // 2, 340)))
        else:
            # Dessiner les lobbies avec clipping
            clip_rect = pygame.Rect(0, 220, SCREEN_WIDTH, SCREEN_HEIGHT - 320)
            self.screen.set_clip(clip_rect)
            for item in self.lobby_items:
                if item.rect.bottom > 220 and item.rect.top < SCREEN_HEIGHT - 100:
                    item.draw(self.screen)
            self.screen.set_clip(None)

    def _draw_create(self):
        """Dessine l'écran de création de lobby."""
        font = pygame.font.SysFont(None, 32)
        label_font = pygame.font.SysFont(None, 28)

        subtitle = font.render("Créer un nouveau lobby", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        # Pseudo
        name_label = label_font.render("Votre pseudo :", True, (180, 180, 200))
        self.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, 170))
        self.name_input.rect.y = 195
        self.name_input.rect.x = SCREEN_WIDTH // 2 - 150
        self.name_input.rect.width = 300
        self.name_input.draw(self.screen)

        # Nom du lobby
        lobby_label = label_font.render("Nom du lobby :", True, (180, 180, 200))
        self.screen.blit(lobby_label, (SCREEN_WIDTH // 2 - 150, 260))
        self.lobby_name_input.rect.y = 285
        self.lobby_name_input.draw(self.screen)

        # Boutons
        self.confirm_create_btn.draw(self.screen)
        self.cancel_btn.draw(self.screen)

    def _draw_in_lobby(self):
        """Dessine l'écran d'attente dans le lobby."""
        font = pygame.font.SysFont(None, 32)
        small_font = pygame.font.SysFont(None, 28)

        # Statut
        if self.client and self.client.is_host:
            status = font.render("Votre lobby - En attente de joueurs", True, (100, 255, 100))
        else:
            status = font.render("Dans le lobby - En attente", True, (100, 200, 255))
        self.screen.blit(status, status.get_rect(center=(SCREEN_WIDTH // 2, 140)))

        # Liste des joueurs
        y = 220
        players_title = font.render("Joueurs :", True, WHITE)
        self.screen.blit(players_title, (SCREEN_WIDTH // 2 - 150, y))
        y += 50

        if self.client:
            for player in self.client.players_in_lobby:
                name = player.get("name", "Joueur")
                player_id = player.get("player_id", 0)
                ready = player.get("ready", False)
                is_me = player_id == self.client.player_id

                color = (100, 255, 100) if ready else (200, 200, 220)
                suffix = ""
                if is_me:
                    suffix = " (vous)"
                if ready:
                    suffix += " ✓"

                text = small_font.render(f"• {name}{suffix}", True, color)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - 130, y))
                y += 35

        # Nombre de joueurs
        count = len(self.client.players_in_lobby) if self.client else 0
        count_text = small_font.render(f"{count}/2 joueurs", True, (150, 150, 180))
        self.screen.blit(count_text, count_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30)))

        # Boutons
        if not self.is_ready:
            self.ready_button.draw(self.screen)
        else:
            ready_text = font.render("En attente de l'autre joueur...", True, (100, 255, 100))
            self.screen.blit(ready_text, ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140)))

        self.leave_lobby_btn.draw(self.screen)

    def get_client(self) -> GameClient:
        """Retourne le client pour l'utiliser dans GameScreen."""
        return self.client
