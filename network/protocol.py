"""Protocole de communication réseau pour le multijoueur."""

import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


class MessageType(Enum):
    # Client -> Serveur (gestion des lobbies)
    LIST_LOBBIES = "LIST_LOBBIES"
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_LOBBY = "JOIN_LOBBY"
    LEAVE_LOBBY = "LEAVE_LOBBY"

    # Client -> Serveur (en jeu)
    INPUT = "INPUT"
    READY = "READY"

    # Serveur -> Client (gestion des lobbies)
    LOBBY_LIST = "LOBBY_LIST"
    LOBBY_CREATED = "LOBBY_CREATED"
    LOBBY_JOINED = "LOBBY_JOINED"
    LOBBY_UPDATE = "LOBBY_UPDATE"
    LOBBY_ERROR = "LOBBY_ERROR"

    # Serveur -> Client (en jeu)
    PLAYER_JOINED = "PLAYER_JOINED"
    PLAYER_LEFT = "PLAYER_LEFT"
    GAME_START = "GAME_START"
    STATE = "STATE"
    EVENT = "EVENT"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"


@dataclass
class LobbyInfo:
    """Informations sur un lobby."""
    lobby_id: str
    name: str
    host_name: str
    player_count: int
    max_players: int
    in_game: bool


@dataclass
class PlayerState:
    """État d'un joueur."""
    player_id: int
    x: float
    y: float
    hp: int
    power_type: str
    invulnerable: bool


@dataclass
class EnemyState:
    """État d'un ennemi."""
    enemy_id: int
    enemy_type: str
    x: float
    y: float
    hp: int


@dataclass
class ProjectileState:
    """État d'un projectile."""
    proj_id: int
    x: float
    y: float
    proj_type: str
    owner: str  # 'player' ou 'enemy'


class Message:
    """Message réseau sérialisable en JSON."""

    def __init__(self, msg_type: MessageType, **data):
        self.type = msg_type
        self.data = data

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            **self.data
        })

    def to_bytes(self) -> bytes:
        # WebSockets gère le framing automatiquement, pas besoin de préfixe de longueur
        json_str = self.to_json()
        return json_str.encode('utf-8')

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        data = json.loads(json_str)
        msg_type = MessageType(data.pop("type"))
        return cls(msg_type, **data)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        json_str = data.decode('utf-8')
        return cls.from_json(json_str)

    def __repr__(self):
        return f"Message({self.type.value}, {self.data})"


# === Messages Client -> Serveur ===

def msg_list_lobbies() -> Message:
    """Demande la liste des lobbies disponibles."""
    return Message(MessageType.LIST_LOBBIES)


def msg_create_lobby(player_name: str, lobby_name: str) -> Message:
    """Crée un nouveau lobby."""
    return Message(MessageType.CREATE_LOBBY, player_name=player_name, lobby_name=lobby_name)


def msg_join_lobby(player_name: str, lobby_id: str) -> Message:
    """Rejoint un lobby existant."""
    return Message(MessageType.JOIN_LOBBY, player_name=player_name, lobby_id=lobby_id)


def msg_leave_lobby() -> Message:
    """Quitte le lobby actuel."""
    return Message(MessageType.LEAVE_LOBBY)


def msg_input(dx: float, dy: float, shoot: bool) -> Message:
    """Envoie les inputs du joueur."""
    return Message(MessageType.INPUT, dx=dx, dy=dy, shoot=shoot)


def msg_ready() -> Message:
    """Signale que le joueur est prêt."""
    return Message(MessageType.READY)


# === Messages Serveur -> Client ===

def msg_lobby_list(lobbies: List[Dict]) -> Message:
    """Envoie la liste des lobbies."""
    return Message(MessageType.LOBBY_LIST, lobbies=lobbies)


def msg_lobby_created(lobby_id: str, player_id: int) -> Message:
    """Confirme la création d'un lobby."""
    return Message(MessageType.LOBBY_CREATED, lobby_id=lobby_id, player_id=player_id)


def msg_lobby_joined(lobby_id: str, player_id: int, players: List[Dict]) -> Message:
    """Confirme l'entrée dans un lobby."""
    return Message(MessageType.LOBBY_JOINED, lobby_id=lobby_id, player_id=player_id, players=players)


def msg_lobby_update(players: List[Dict]) -> Message:
    """Met à jour l'état du lobby (joueurs, etc.)."""
    return Message(MessageType.LOBBY_UPDATE, players=players)


def msg_lobby_error(error: str) -> Message:
    """Signale une erreur liée au lobby."""
    return Message(MessageType.LOBBY_ERROR, error=error)


def msg_player_joined(player_id: int, name: str) -> Message:
    """Un joueur a rejoint le lobby."""
    return Message(MessageType.PLAYER_JOINED, player_id=player_id, name=name)


def msg_player_left(player_id: int) -> Message:
    """Un joueur a quitté le lobby."""
    return Message(MessageType.PLAYER_LEFT, player_id=player_id)


def msg_game_start() -> Message:
    """La partie commence."""
    return Message(MessageType.GAME_START)


def msg_state(
    players: List[Dict],
    enemies: List[Dict],
    projectiles: List[Dict],
    enemy_projectiles: List[Dict],
    powerups: List[Dict],
    explosions: List[Dict],
    timer: int
) -> Message:
    """État complet du jeu."""
    return Message(
        MessageType.STATE,
        players=players,
        enemies=enemies,
        projectiles=projectiles,
        enemy_projectiles=enemy_projectiles,
        powerups=powerups,
        explosions=explosions,
        timer=timer
    )


def msg_event(kind: str, **kwargs) -> Message:
    """Événement de jeu (explosion, powerup, etc.)."""
    return Message(MessageType.EVENT, kind=kind, **kwargs)


def msg_game_over() -> Message:
    """La partie est perdue."""
    return Message(MessageType.GAME_OVER)


def msg_victory() -> Message:
    """La partie est gagnée."""
    return Message(MessageType.VICTORY)
