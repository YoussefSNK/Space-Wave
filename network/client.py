"""Client réseau pour le multijoueur avec gestion des lobbies."""

import asyncio
import threading
import websockets
from typing import Optional, Callable, Dict, List, Any
from queue import Queue, Empty

from network.protocol import (
    Message, MessageType,
    msg_list_lobbies, msg_create_lobby, msg_join_lobby, msg_leave_lobby,
    msg_input, msg_ready
)


class GameClient:
    """Client de jeu pour se connecter au serveur central."""

    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.player_id: Optional[int] = None
        self.lobby_id: Optional[str] = None

        # Liste des lobbies disponibles
        self.lobbies: List[Dict] = []
        self.lobbies_updated = False

        # État du lobby actuel
        self.players_in_lobby: List[Dict] = []
        self.is_host = False
        self.lobby_error: Optional[str] = None

        # État du jeu
        self.game_state: Dict[str, Any] = {
            "players": [],
            "enemies": [],
            "projectiles": [],
            "enemy_projectiles": [],
            "powerups": [],
            "explosions": [],
            "timer": 0
        }
        self.game_started = False
        self.game_over = False
        self.victory = False

        # File de messages à envoyer
        self._send_queue: Queue = Queue()

        # Thread pour le réseau
        self._network_thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False

    def connect(self, host: str, port: int) -> bool:
        """Se connecte au serveur (bloquant au démarrage)."""
        self._running = True
        self._network_thread = threading.Thread(
            target=self._run_network_loop,
            args=(host, port),
            daemon=True
        )
        self._network_thread.start()

        # Attendre la connexion (avec timeout)
        import time
        for _ in range(50):  # 5 secondes max
            if self.connected or not self._running:
                break
            time.sleep(0.1)

        return self.connected

    def _run_network_loop(self, host: str, port: int):
        """Exécute la boucle asyncio dans un thread séparé."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(
                self._async_connect(host, port)
            )
        except Exception as e:
            print(f"Erreur réseau: {e}")
        finally:
            self._loop.close()
            self.connected = False
            self._running = False

    async def _async_connect(self, host: str, port: int):
        """Connexion asynchrone au serveur."""
        try:
            # Détecter si l'host est une URL complète (commence par ws:// ou wss://)
            if host.startswith("ws://") or host.startswith("wss://"):
                uri = host  # Utiliser l'URL complète fournie
            # Détecter si c'est une URL HTTPS/render (contient .onrender.com, .herokuapp.com, etc.)
            elif ".onrender.com" in host or ".herokuapp.com" in host or host.startswith("https://"):
                # Nettoyer l'URL si elle commence par https://
                clean_host = host.replace("https://", "").replace("http://", "")
                uri = f"wss://{clean_host}"  # Utiliser WSS pour les services cloud
            else:
                # Connexion locale ou par IP
                uri = f"ws://{host}:{port}"

            self.websocket = await websockets.connect(uri)
            self.connected = True
            print(f"Connecté à {uri}")

            # Lancer les tâches de réception et d'envoi
            recv_task = asyncio.create_task(self._receive_loop())
            send_task = asyncio.create_task(self._send_loop())

            await asyncio.gather(recv_task, send_task)

        except ConnectionRefusedError:
            print(f"Impossible de se connecter à {host}")
            self._running = False
        except Exception as e:
            print(f"Erreur connexion: {e}")
            self._running = False

    async def _receive_loop(self):
        """Boucle de réception des messages."""
        try:
            async for message in self.websocket:
                # WebSockets reçoit directement les messages complets
                msg = Message.from_bytes(message.encode('utf-8') if isinstance(message, str) else message)
                self._process_message(msg)

        except asyncio.CancelledError:
            pass
        except websockets.exceptions.ConnectionClosed:
            print("Connexion fermée par le serveur")
        except Exception as e:
            print(f"Erreur réception: {e}")
        finally:
            self.connected = False
            self._running = False

    async def _send_loop(self):
        """Boucle d'envoi des messages."""
        try:
            while self._running and self.connected:
                try:
                    msg = self._send_queue.get_nowait()
                    await self._async_send(msg)
                except Empty:
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Erreur envoi: {e}")

    async def _async_send(self, msg: Message):
        """Envoie un message au serveur."""
        if self.websocket:
            await self.websocket.send(msg.to_bytes())

    def _process_message(self, msg: Message):
        """Traite un message reçu du serveur."""
        # Debug: afficher tous les messages reçus
        print(f"[CLIENT] Message reçu: {msg.type.value}")

        # === Gestion des lobbies ===

        if msg.type == MessageType.LOBBY_LIST:
            self.lobbies = msg.data.get("lobbies", [])
            self.lobbies_updated = True

        elif msg.type == MessageType.LOBBY_CREATED:
            self.lobby_id = msg.data.get("lobby_id")
            self.player_id = msg.data.get("player_id")
            self.is_host = True
            self.players_in_lobby = [{"player_id": self.player_id, "name": "Vous", "ready": False}]
            print(f"Lobby créé: {self.lobby_id}")

        elif msg.type == MessageType.LOBBY_JOINED:
            self.lobby_id = msg.data.get("lobby_id")
            self.player_id = msg.data.get("player_id")
            self.players_in_lobby = msg.data.get("players", [])
            self.is_host = False
            print(f"Rejoint le lobby: {self.lobby_id}")

        elif msg.type == MessageType.LOBBY_UPDATE:
            self.players_in_lobby = msg.data.get("players", [])

        elif msg.type == MessageType.LOBBY_ERROR:
            self.lobby_error = msg.data.get("error", "Erreur inconnue")
            print(f"Erreur lobby: {self.lobby_error}")

        elif msg.type == MessageType.PLAYER_JOINED:
            player = {
                "player_id": msg.data.get("player_id"),
                "name": msg.data.get("name"),
                "ready": False
            }
            self.players_in_lobby.append(player)
            print(f"Joueur {player['name']} a rejoint")

        elif msg.type == MessageType.PLAYER_LEFT:
            player_id = msg.data.get("player_id")
            self.players_in_lobby = [
                p for p in self.players_in_lobby
                if p.get("player_id") != player_id
            ]
            print(f"Joueur {player_id} a quitté")

        # === Gestion du jeu ===

        elif msg.type == MessageType.GAME_START:
            self.game_started = True
            print("La partie commence !")

        elif msg.type == MessageType.STATE:
            self.game_state = {
                "players": msg.data.get("players", []),
                "enemies": msg.data.get("enemies", []),
                "projectiles": msg.data.get("projectiles", []),
                "enemy_projectiles": msg.data.get("enemy_projectiles", []),
                "powerups": msg.data.get("powerups", []),
                "explosions": msg.data.get("explosions", []),
                "timer": msg.data.get("timer", 0)
            }

        elif msg.type == MessageType.GAME_OVER:
            self.game_over = True
            print("Game Over !")

        elif msg.type == MessageType.VICTORY:
            self.victory = True
            print("Victoire !")

    # === API pour le lobby ===

    def request_lobby_list(self):
        """Demande la liste des lobbies disponibles."""
        if self.connected:
            self.lobbies_updated = False
            self._send_queue.put(msg_list_lobbies())

    def create_lobby(self, player_name: str, lobby_name: str):
        """Crée un nouveau lobby."""
        if self.connected:
            self.lobby_error = None
            self._send_queue.put(msg_create_lobby(player_name, lobby_name))

    def join_lobby(self, player_name: str, lobby_id: str):
        """Rejoint un lobby existant."""
        if self.connected:
            self.lobby_error = None
            self._send_queue.put(msg_join_lobby(player_name, lobby_id))

    def leave_lobby(self):
        """Quitte le lobby actuel."""
        if self.connected:
            self._send_queue.put(msg_leave_lobby())
            self.lobby_id = None
            self.players_in_lobby = []

    def send_ready(self):
        """Signale que le joueur est prêt."""
        if self.connected:
            self._send_queue.put(msg_ready())

    # === API pour le jeu ===

    def send_input(self, dx: float, dy: float, shoot: bool):
        """Envoie les inputs du joueur au serveur."""
        if self.connected:
            self._send_queue.put(msg_input(dx, dy, shoot))

    def disconnect(self):
        """Se déconnecte du serveur."""
        if self.lobby_id:
            self.leave_lobby()
        self._running = False
        self.connected = False

    # === Helpers ===

    def get_player_state(self, player_id: int) -> Optional[Dict]:
        """Récupère l'état d'un joueur."""
        for player in self.game_state.get("players", []):
            if player.get("player_id") == player_id:
                return player
        return None

    def get_local_player_state(self) -> Optional[Dict]:
        """Récupère l'état du joueur local."""
        if self.player_id is not None:
            return self.get_player_state(self.player_id)
        return None

    def get_remote_player_state(self) -> Optional[Dict]:
        """Récupère l'état du joueur distant."""
        for player in self.game_state.get("players", []):
            if player.get("player_id") != self.player_id:
                return player
        return None

    def in_lobby(self) -> bool:
        """Vérifie si le joueur est dans un lobby."""
        return self.lobby_id is not None
