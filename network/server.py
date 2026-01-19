"""Serveur de jeu multijoueur avec gestion des lobbies."""

import asyncio
import random
import uuid
import pygame
import sys
import os
import websockets
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, field

# Ajouter le répertoire parent au PYTHONPATH pour trouver config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from systems.level import Level
from entities.player import Player
from entities.enemy import Enemy, ShootingEnemy
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6
from entities.powerup import PowerUp
from entities.projectiles import (
    Projectile, HomingProjectile, SplittingProjectile,
    MirrorProjectile, BlackHoleProjectile, PulseWaveProjectile
)
from graphics.effects import Explosion
from network.protocol import (
    Message, MessageType,
    msg_lobby_list, msg_lobby_created, msg_lobby_joined, msg_lobby_update, msg_lobby_error,
    msg_player_joined, msg_player_left,
    msg_game_start, msg_state, msg_event, msg_game_over, msg_victory
)


@dataclass
class ServerPlayer:
    """État d'un joueur côté serveur."""
    player_id: int
    name: str
    websocket: websockets.WebSocketServerProtocol
    lobby_id: Optional[str] = None
    player: Player = field(default=None)
    dx: float = 0
    dy: float = 0
    shoot: bool = False
    ready: bool = False

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "name": self.name,
            "x": self.player.rect.centerx if self.player else 0,
            "y": self.player.rect.centery if self.player else 0,
            "hp": self.player.hp if self.player else 0,
            "power_type": self.player.power_type if self.player else "normal",
            "invulnerable": self.player.invulnerable if self.player else False,
            "ready": self.ready,
            "is_crashing": self.player.is_crashing if self.player else False,
            "crash_timer": self.player.crash_timer if (self.player and self.player.is_crashing) else 0,
            "crash_rotation": self.player.crash_rotation if (self.player and self.player.is_crashing) else 0,
        }


@dataclass
class GameLobby:
    """Un lobby de jeu hébergé sur le serveur."""
    lobby_id: str
    name: str
    host_id: int
    max_players: int = 2
    players: Dict[int, ServerPlayer] = field(default_factory=dict)

    # État du jeu (None si pas encore démarré)
    level: Level = None
    projectiles: List = field(default_factory=list)
    enemy_projectiles: List = field(default_factory=list)
    explosions: List = field(default_factory=list)
    powerups: List = field(default_factory=list)

    game_started: bool = False
    game_over: bool = False
    victory: bool = False

    def to_dict(self):
        host = self.players.get(self.host_id)
        return {
            "lobby_id": self.lobby_id,
            "name": self.name,
            "host_name": host.name if host else "???",
            "player_count": len(self.players),
            "max_players": self.max_players,
            "in_game": self.game_started
        }

    def get_players_info(self):
        return [{"player_id": p.player_id, "name": p.name, "ready": p.ready}
                for p in self.players.values()]


class GameServer:
    """Serveur central gérant plusieurs lobbies de jeu."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        self.host = host
        self.port = port

        # Connexions clients
        self.clients: Dict[int, ServerPlayer] = {}
        self.next_player_id = 1

        # Lobbies actifs
        self.lobbies: Dict[str, GameLobby] = {}

        self.running = False
        self.tick_rate = 60

    async def start(self):
        """Démarre le serveur."""
        self.running = True
        print(f"Serveur WebSocket démarré sur ws://{self.host}:{self.port}")
        print("En attente de connexions...")

        # Lancer la boucle de jeu pour tous les lobbies
        game_task = asyncio.create_task(self._game_loop())

        # Démarrer le serveur WebSocket
        async with websockets.serve(self._handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol):
        """Gère la connexion d'un client."""
        player_id = self.next_player_id
        self.next_player_id += 1

        addr = websocket.remote_address
        print(f"Nouvelle connexion #{player_id} de {addr}")

        # Créer le joueur (sans nom pour l'instant)
        player = ServerPlayer(
            player_id=player_id,
            name=f"Joueur{player_id}",
            websocket=websocket
        )
        self.clients[player_id] = player

        try:
            async for message in websocket:
                # WebSockets reçoit directement les messages complets
                msg = Message.from_bytes(message.encode('utf-8') if isinstance(message, str) else message)
                await self._process_message(msg, player_id)

        except websockets.exceptions.ConnectionClosed:
            print(f"Client #{player_id}: connexion fermée")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Erreur client #{player_id}: {e}")
        finally:
            await self._disconnect_player(player_id)
            print(f"Client #{player_id} déconnecté")

    async def _process_message(self, msg: Message, player_id: int):
        """Traite un message reçu d'un client."""
        player = self.clients.get(player_id)
        if not player:
            return

        if msg.type == MessageType.LIST_LOBBIES:
            # Envoyer la liste des lobbies disponibles
            lobbies = [lobby.to_dict() for lobby in self.lobbies.values()
                      if not lobby.game_started and len(lobby.players) < lobby.max_players]
            await self._send(player.websocket, msg_lobby_list(lobbies))

        elif msg.type == MessageType.CREATE_LOBBY:
            player_name = msg.data.get("player_name", f"Joueur{player_id}")
            lobby_name = msg.data.get("lobby_name", f"Partie de {player_name}")

            # Quitter l'ancien lobby si besoin
            if player.lobby_id:
                await self._leave_lobby(player_id)

            # Créer le nouveau lobby
            lobby_id = str(uuid.uuid4())[:8]
            lobby = GameLobby(
                lobby_id=lobby_id,
                name=lobby_name,
                host_id=player_id
            )
            self.lobbies[lobby_id] = lobby

            # Ajouter le joueur au lobby
            player.name = player_name
            player.lobby_id = lobby_id
            player.ready = False
            lobby.players[player_id] = player

            await self._send(player.websocket, msg_lobby_created(lobby_id, player_id))
            print(f"Lobby '{lobby_name}' créé par {player_name}")

        elif msg.type == MessageType.JOIN_LOBBY:
            player_name = msg.data.get("player_name", f"Joueur{player_id}")
            lobby_id = msg.data.get("lobby_id")

            lobby = self.lobbies.get(lobby_id)
            if not lobby:
                await self._send(player.websocket, msg_lobby_error("Lobby introuvable"))
                return

            if lobby.game_started:
                await self._send(player.websocket, msg_lobby_error("Partie déjà en cours"))
                return

            if len(lobby.players) >= lobby.max_players:
                await self._send(player.websocket, msg_lobby_error("Lobby plein"))
                return

            # Quitter l'ancien lobby si besoin
            if player.lobby_id:
                await self._leave_lobby(player_id)

            # Rejoindre le lobby
            player.name = player_name
            player.lobby_id = lobby_id
            player.ready = False
            lobby.players[player_id] = player

            # Notifier tous les joueurs du lobby
            await self._send(player.websocket, msg_lobby_joined(lobby_id, player_id, lobby.get_players_info()))
            await self._broadcast_to_lobby(lobby, msg_player_joined(player_id, player_name), exclude=player_id)
            print(f"{player_name} a rejoint le lobby '{lobby.name}'")

        elif msg.type == MessageType.LEAVE_LOBBY:
            await self._leave_lobby(player_id)

        elif msg.type == MessageType.READY:
            if player.lobby_id:
                lobby = self.lobbies.get(player.lobby_id)
                if lobby and not lobby.game_started:
                    player.ready = True
                    print(f"{player.name} est prêt")

                    # Notifier les autres joueurs
                    await self._broadcast_to_lobby(lobby, msg_lobby_update(lobby.get_players_info()))

                    # Vérifier si tous les joueurs sont prêts
                    if len(lobby.players) >= 2 and all(p.ready for p in lobby.players.values()):
                        await self._start_game(lobby)

        elif msg.type == MessageType.INPUT:
            if player.lobby_id:
                lobby = self.lobbies.get(player.lobby_id)
                if lobby and lobby.game_started:
                    player.dx = msg.data.get("dx", 0)
                    player.dy = msg.data.get("dy", 0)
                    player.shoot = msg.data.get("shoot", False)

    async def _leave_lobby(self, player_id: int):
        """Fait quitter un joueur de son lobby."""
        player = self.clients.get(player_id)
        if not player or not player.lobby_id:
            return

        lobby = self.lobbies.get(player.lobby_id)
        if not lobby:
            player.lobby_id = None
            return

        # Retirer le joueur du lobby
        if player_id in lobby.players:
            del lobby.players[player_id]

        player.lobby_id = None
        player.ready = False
        player.player = None

        # Notifier les autres joueurs
        print(f"[DEBUG] Envoi PLAYER_LEFT pour joueur #{player_id}")
        await self._broadcast_to_lobby(lobby, msg_player_left(player_id))

        # Supprimer le lobby s'il est vide
        if not lobby.players:
            del self.lobbies[lobby.lobby_id]
            print(f"Lobby '{lobby.name}' supprimé (vide)")
        elif lobby.host_id == player_id:
            # Transférer l'hôte au premier joueur restant
            new_host_id = next(iter(lobby.players.keys()))
            lobby.host_id = new_host_id
            print(f"Nouvel hôte du lobby: Joueur #{new_host_id}")

    async def _disconnect_player(self, player_id: int):
        """Déconnecte un joueur du serveur."""
        await self._leave_lobby(player_id)
        if player_id in self.clients:
            del self.clients[player_id]

    async def _start_game(self, lobby: GameLobby):
        """Démarre une partie dans un lobby."""
        print(f"Démarrage de la partie dans le lobby '{lobby.name}'")

        # Initialiser le niveau
        lobby.level = Level()
        lobby.projectiles = []
        lobby.enemy_projectiles = []
        lobby.explosions = []
        lobby.powerups = []
        lobby.game_over = False
        lobby.victory = False

        # Créer les joueurs AVANT de démarrer le jeu (évite condition de course)
        # Mode headless=True car le serveur n'a pas besoin des sprites
        positions = [
            (SCREEN_WIDTH // 3, SCREEN_HEIGHT - 100),
            (2 * SCREEN_WIDTH // 3, SCREEN_HEIGHT - 100)
        ]
        for i, (pid, sp) in enumerate(lobby.players.items()):
            x, y = positions[i] if i < len(positions) else (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
            sp.player = Player(x, y, player_id=i + 1, is_local=True, headless=True)

        # Marquer le jeu comme démarré seulement après avoir créé les joueurs
        lobby.game_started = True

        await self._broadcast_to_lobby(lobby, msg_game_start())

    async def _game_loop(self):
        """Boucle principale du jeu pour tous les lobbies."""
        while self.running:
            for lobby in list(self.lobbies.values()):
                if lobby.game_started and not lobby.game_over and not lobby.victory:
                    self._update_lobby_game(lobby)
                    await self._broadcast_lobby_state(lobby)

                    if self._check_game_over(lobby):
                        lobby.game_over = True
                        print(f"[DEBUG] GAME_OVER envoyé au lobby '{lobby.name}'")
                        await self._broadcast_to_lobby(lobby, msg_game_over())
                    elif self._check_victory(lobby):
                        lobby.victory = True
                        await self._broadcast_to_lobby(lobby, msg_victory())

            await asyncio.sleep(1 / self.tick_rate)

    def _update_lobby_game(self, lobby: GameLobby):
        """Met à jour la logique du jeu pour un lobby."""
        # Mettre à jour les joueurs
        for sp in lobby.players.values():
            if sp.player:
                if sp.player.is_crashing:
                    # Mettre à jour l'animation de crash
                    sp.player.update()
                elif sp.player.hp > 0:
                    # Logique normale
                    sp.player.dx = sp.dx
                    sp.player.dy = sp.dy
                    sp.player.update()

                    if sp.shoot:
                        sp.player.shoot(lobby.projectiles)

        # Mettre à jour le niveau
        lobby.level.update()

        # Mettre à jour les ennemis
        self._update_enemies(lobby)

        # Mettre à jour les projectiles
        self._update_projectiles(lobby)

        # Mettre à jour les powerups
        self._update_powerups(lobby)

        # Mettre à jour les explosions
        self._update_explosions(lobby)

        # Vérifier les collisions
        self._check_collisions(lobby)

    def _update_enemies(self, lobby: GameLobby):
        """Met à jour les ennemis."""
        player_centers = [
            sp.player.rect.center for sp in lobby.players.values()
            if sp.player and sp.player.hp > 0
        ]
        if not player_centers:
            return

        for enemy in lobby.level.enemies[:]:
            # Cibler le joueur le plus proche
            target = min(player_centers, key=lambda p: abs(p[0] - enemy.rect.centerx))

            if isinstance(enemy, Boss6):
                result = enemy.update(target, lobby.enemy_projectiles)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 40, 200, 1200)
                    lobby.victory = True
            elif isinstance(enemy, Boss5):
                result = enemy.update(target, lobby.enemy_projectiles)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 30, 180, 1000)
                    lobby.level.boss5_defeated = True
            elif isinstance(enemy, Boss4):
                result = enemy.update(target, lobby.enemy_projectiles)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 20, 160, 800)
                    lobby.level.boss4_defeated = True
            elif isinstance(enemy, Boss3):
                result = enemy.update(target, lobby.enemy_projectiles)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 12, 140, 700)
                    lobby.level.boss3_defeated = True
            elif isinstance(enemy, Boss2):
                result = enemy.update(target, lobby.enemy_projectiles)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 8, 120, 600)
                    lobby.level.boss2_defeated = True
            elif isinstance(enemy, Boss):
                # Pour Boss1, passer les positions des deux joueurs séparément
                # On récupère les joueurs vivants dans l'ordre
                alive_players = [sp for sp in sorted(lobby.players.values(), key=lambda p: p.player_id)
                                if sp.player and sp.player.hp > 0]
                player1_pos = alive_players[0].player.rect.center if len(alive_players) > 0 else None
                player2_pos = alive_players[1].player.rect.center if len(alive_players) > 1 else None
                result = enemy.update(player1_pos, lobby.enemy_projectiles, player2_pos)
                if result is True:
                    lobby.level.enemies.remove(enemy)
                    self._create_boss_explosions(lobby, enemy, 5, 100, 500)
                    lobby.level.boss1_defeated = True
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(target, lobby.enemy_projectiles)

    def _create_boss_explosions(self, lobby: GameLobby, enemy, count: int, size: int, duration: int):
        """Crée des explosions à la mort d'un boss."""
        for _ in range(count):
            rand_x = enemy.rect.left + random.randint(0, size)
            rand_y = enemy.rect.top + random.randint(0, size)
            lobby.explosions.append({
                "x": rand_x,
                "y": rand_y,
                "duration": duration,
                "start_time": pygame.time.get_ticks()
            })

    def _update_projectiles(self, lobby: GameLobby):
        """Met à jour tous les projectiles."""
        # Projectiles des joueurs
        for proj in lobby.projectiles:
            proj.update()
        lobby.projectiles = [p for p in lobby.projectiles if p.rect.bottom > 0]

        # Projectiles ennemis
        player_centers = [
            sp.player.rect.center for sp in lobby.players.values()
            if sp.player and sp.player.hp > 0
        ]

        for e_proj in lobby.enemy_projectiles:
            if isinstance(e_proj, HomingProjectile) and player_centers:
                target = min(player_centers, key=lambda p: abs(p[0] - e_proj.rect.centerx))
                e_proj.update(target)
            else:
                e_proj.update()

        # Gérer les projectiles qui se divisent
        new_split = []
        for e_proj in lobby.enemy_projectiles:
            if isinstance(e_proj, SplittingProjectile) and e_proj.should_split():
                new_split.extend(e_proj.split())
            elif isinstance(e_proj, MirrorProjectile) and e_proj.should_split():
                new_split.extend(e_proj.split())
        lobby.enemy_projectiles.extend(new_split)

        # Filtrer projectiles hors écran et expirés
        lobby.enemy_projectiles = [p for p in lobby.enemy_projectiles if (
            p.rect.top < SCREEN_HEIGHT and p.rect.left < SCREEN_WIDTH and
            p.rect.right > 0 and p.rect.bottom > 0 and
            not (isinstance(p, HomingProjectile) and p.is_expired()) and
            not (isinstance(p, BlackHoleProjectile) and p.is_expired()) and
            not (isinstance(p, PulseWaveProjectile) and p.is_expired())
        )]

    def _update_powerups(self, lobby: GameLobby):
        """Met à jour les powerups."""
        for powerup in lobby.powerups:
            powerup.update()
        lobby.powerups = [p for p in lobby.powerups if p.rect.top < SCREEN_HEIGHT]

    def _update_explosions(self, lobby: GameLobby):
        """Met à jour les explosions."""
        current_time = pygame.time.get_ticks()
        lobby.explosions = [
            exp for exp in lobby.explosions
            if current_time - exp["start_time"] < exp["duration"]
        ]

    def _check_collisions(self, lobby: GameLobby):
        """Vérifie toutes les collisions."""
        # Projectiles joueurs vs ennemis
        for proj in lobby.projectiles[:]:
            for enemy in lobby.level.enemies[:]:
                if proj.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        if enemy.is_dying:
                            continue
                        enemy.take_damage(1)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        # Créer une explosion
                        lobby.explosions.append({
                            "x": enemy.rect.centerx,
                            "y": enemy.rect.centery,
                            "duration": 300,
                            "start_time": pygame.time.get_ticks()
                        })

                        # Drop de powerup
                        if hasattr(enemy, 'drops_powerup') and enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, random.choice(power_types))
                            lobby.powerups.append(powerup)
                        lobby.level.enemies.remove(enemy)

                    if proj in lobby.projectiles:
                        lobby.projectiles.remove(proj)
                    break

        # Projectiles ennemis vs joueurs
        for e_proj in lobby.enemy_projectiles[:]:
            for sp in lobby.players.values():
                if not sp.player or sp.player.invulnerable or sp.player.hp <= 0:
                    continue

                hit = False
                if isinstance(e_proj, PulseWaveProjectile):
                    if e_proj.check_collision(sp.player.rect):
                        hit = True
                elif e_proj.rect.colliderect(sp.player.rect):
                    hit = True
                    if e_proj in lobby.enemy_projectiles:
                        lobby.enemy_projectiles.remove(e_proj)

                if hit:
                    sp.player.hp -= 1
                    if sp.player.hp <= 0 and not sp.player.is_crashing:
                        sp.player.start_crash()
                    else:
                        sp.player.invulnerable = True
                        sp.player.invuln_start = pygame.time.get_ticks()
                    break

        # Ennemis vs joueurs
        for enemy in lobby.level.enemies:
            for sp in lobby.players.values():
                if not sp.player or sp.player.invulnerable or sp.player.hp <= 0:
                    continue
                if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                    continue

                if enemy.rect.colliderect(sp.player.rect):
                    damage = 3 if isinstance(enemy, Boss4) and enemy.charging else 1
                    sp.player.hp -= damage
                    if sp.player.hp <= 0 and not sp.player.is_crashing:
                        sp.player.start_crash()
                    else:
                        sp.player.invulnerable = True
                        sp.player.invuln_start = pygame.time.get_ticks()

                    # Explosion de contact
                    lobby.explosions.append({
                        "x": (sp.player.rect.centerx + enemy.rect.centerx) // 2,
                        "y": (sp.player.rect.centery + enemy.rect.centery) // 2,
                        "duration": 300,
                        "start_time": pygame.time.get_ticks()
                    })

        # Powerups vs joueurs
        for powerup in lobby.powerups[:]:
            for sp in lobby.players.values():
                if sp.player and powerup.rect.colliderect(sp.player.rect):
                    sp.player.apply_powerup(powerup.power_type)
                    if powerup in lobby.powerups:
                        lobby.powerups.remove(powerup)
                    break

        # Laser Boss3
        for enemy in lobby.level.enemies:
            if isinstance(enemy, Boss3) and enemy.laser_active:
                laser_rect = pygame.Rect(enemy.laser_target_x - 25, 0, 50, SCREEN_HEIGHT)
                for sp in lobby.players.values():
                    if sp.player and not sp.player.invulnerable and sp.player.hp > 0:
                        if sp.player.rect.colliderect(laser_rect):
                            sp.player.hp -= 2
                            if sp.player.hp <= 0 and not sp.player.is_crashing:
                                sp.player.start_crash()
                            else:
                                sp.player.invulnerable = True
                                sp.player.invuln_start = pygame.time.get_ticks()

    def _check_game_over(self, lobby: GameLobby) -> bool:
        """Vérifie si tous les joueurs sont morts ET ont terminé leur animation de crash."""
        for sp in lobby.players.values():
            if sp.player is None:
                continue
            # Le joueur est considéré "vivant" s'il a des HP ou si son crash n'est pas terminé
            if sp.player.hp > 0 or sp.player.is_crashing:
                return False
        return True

    def _check_victory(self, lobby: GameLobby) -> bool:
        """Vérifie si le Boss 6 est vaincu."""
        if not lobby.level:
            return False
        return (
            lobby.level.boss5_defeated and
            lobby.level.boss6_spawned and
            not any(isinstance(e, Boss6) for e in lobby.level.enemies)
        )

    async def _broadcast_lobby_state(self, lobby: GameLobby):
        """Envoie l'état complet du jeu à tous les joueurs d'un lobby."""
        # Sérialiser les joueurs
        players_data = [sp.to_dict() for sp in lobby.players.values()]

        # Sérialiser les ennemis
        enemies_data = []
        for enemy in lobby.level.enemies:
            enemy_type = type(enemy).__name__
            enemy_data = {
                "enemy_id": id(enemy),
                "enemy_type": enemy_type,
                "x": enemy.rect.centerx,
                "y": enemy.rect.centery,
                "hp": getattr(enemy, 'hp', 1),
                "is_dying": getattr(enemy, 'is_dying', False)
            }
            # Données d'animation pour tous les boss
            if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                enemy_data["damage_animation_active"] = getattr(enemy, 'damage_animation_active', False)
                enemy_data["animation_active"] = getattr(enemy, 'animation_active', False)
            # Données spécifiques aux boss
            if isinstance(enemy, Boss3):
                enemy_data["laser_active"] = enemy.laser_active
                enemy_data["laser_target_x"] = getattr(enemy, 'laser_target_x', 0)
                enemy_data["laser_warning"] = getattr(enemy, 'laser_warning', False)
            if isinstance(enemy, Boss4):
                enemy_data["charging"] = getattr(enemy, 'charging', False)
            enemies_data.append(enemy_data)

        # Sérialiser les projectiles
        projs_data = [{
            "proj_id": id(proj),
            "x": proj.rect.centerx,
            "y": proj.rect.centery,
            "proj_type": type(proj).__name__
        } for proj in lobby.projectiles]

        enemy_projs_data = [{
            "proj_id": id(proj),
            "x": proj.rect.centerx,
            "y": proj.rect.centery,
            "proj_type": type(proj).__name__,
            "radius": getattr(proj, 'radius', 5)
        } for proj in lobby.enemy_projectiles]

        # Sérialiser les powerups
        powerups_data = [{
            "x": powerup.rect.centerx,
            "y": powerup.rect.centery,
            "power_type": powerup.power_type
        } for powerup in lobby.powerups]

        # Explosions (déjà en format dict)
        explosions_data = lobby.explosions

        msg = msg_state(
            players=players_data,
            enemies=enemies_data,
            projectiles=projs_data,
            enemy_projectiles=enemy_projs_data,
            powerups=powerups_data,
            explosions=explosions_data,
            timer=lobby.level.timer if lobby.level else 0
        )
        await self._broadcast_to_lobby(lobby, msg)

    async def _broadcast_to_lobby(self, lobby: GameLobby, msg: Message, exclude: Optional[int] = None):
        """Envoie un message à tous les joueurs d'un lobby."""
        for player_id, player in list(lobby.players.items()):
            if player_id != exclude:
                try:
                    await self._send(player.websocket, msg)
                except Exception as e:
                    print(f"Erreur envoi à joueur #{player_id}: {e}")

    async def _send(self, websocket: websockets.WebSocketServerProtocol, msg: Message):
        """Envoie un message à un client."""
        await websocket.send(msg.to_bytes())


async def run_server(host: str = "0.0.0.0", port: int = 5555):
    """Lance le serveur de jeu."""
    # Initialiser pygame avec un display minimal (nécessaire pour convert_alpha)
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)

    server = GameServer(host, port)
    await server.start()


if __name__ == "__main__":
    import os
    # Sur Render, utiliser la variable d'environnement PORT
    port = int(os.environ.get("PORT", 5555))
    asyncio.run(run_server(port=port))
