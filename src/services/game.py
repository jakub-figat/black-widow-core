from typing import Any, Optional
from uuid import uuid4

from src.core.game import Game
from src.data_access.exceptions import DoesNotExist
from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.schemas.game import GameModel
from src.schemas.lobby import LobbyModel
from src.schemas.user import UserModel
from src.schemas.websocket import GetGameDetailPayload
from src.services.exceptions import GameServiceException


class GameService:
    def __init__(
        self, game_data_access: GameDataAccess, user_data_access: UserDataAccess, lobby_data_access: LobbyDataAccess
    ) -> None:
        self.game_data_access = game_data_access
        self.user_data_access = user_data_access
        self.lobby_data_access = lobby_data_access

    def create_lobby(self, user: UserModel, max_players: int = 3) -> LobbyModel:
        lobby = LobbyModel(lobby_id=str(uuid4()), users=[user.email], max_players=max_players)
        self.lobby_data_access.save(model=lobby)

        user.lobbies_ids.append(lobby.lobby_id)
        self.user_data_access.save(model=user)

        return lobby

    def add_user_to_lobby(self, lobby_id: str, user: UserModel) -> Optional[GameModel]:
        lobby_key = {"pk": "lobby", "sk": f"lobby#{lobby_id}"}
        lobby = self.lobby_data_access.get(**lobby_key)
        if lobby is None:
            raise DoesNotExist(f"Lobby with id {lobby_id} does not exist.")

        if user.email in lobby.users:
            raise GameServiceException(f"User {user.email} is already in lobby {lobby.lobby_id}")

        if len(lobby.users) + 1 == lobby.max_players:  # lobby will be full, we can start the game
            users = [self.user_data_access.get(pk=f"user", sk=f"user#{email}") for email in lobby.users]
            game_id = str(uuid4())
            for user_ in users:
                user_.lobbies_ids.remove(lobby_id)

            for user_ in users + [user]:
                user_.games_ids.append(game_id)

            self.user_data_access.bulk_save(models=users + [user])
            self.lobby_data_access.delete(**lobby_key)

            game = GameModel(
                game_id=game_id, game=Game.start_game(users=[user.email for user in users] + [user.email])
            )
            self.game_data_access.save(model=game)

            return game

        lobby.users.append(user.email)
        self.lobby_data_access.save(model=lobby)

        user.lobbies_ids.append(lobby.lobby_id)
        self.user_data_access.save(model=user)

    def remove_user_from_lobby(self, lobby_id: str, user: UserModel) -> bool:
        lobby = self.lobby_data_access.get(pk="lobby", sk=f"lobby#{lobby_id}")
        if lobby is None:
            raise DoesNotExist(f"Lobby with id {lobby_id} does not exist.")

        if user.email not in lobby.users:
            raise GameServiceException(f"User {user.email} not found in lobby {lobby.lobby_id}")

        lobby.users.remove(user.email)

        if len(lobby.users) == 0:
            self.lobby_data_access.delete(**lobby.key)
        else:
            self.lobby_data_access.save(model=lobby)

        user.lobbies_ids.remove(lobby_id)
        self.user_data_access.save(model=user)

        return len(lobby.users) == 0

    def get_game_with_user(self, game_id: str, user_id: str) -> GameModel:
        game = self.game_data_access.get(pk="game", sk=f"game#{game_id}")
        if game is None:
            raise DoesNotExist(f"You do not participate in game with id {game_id}")

        if user_id not in game.game.state.users:
            raise GameServiceException(f"You do not participate in game with id {game_id}")

        return game

    def dispatch_game_action(self, game_id: str, user: UserModel, payload: dict[str, Any]) -> None:
        game_model = self.game_data_access.get(pk=f"game", sk=f"game#{game_id}")
        if game_model is None:
            raise DoesNotExist(f"Game with id {game_id} does not exist")
        payload = game_model.game.current_step.payload_class(**payload, user=user.email)
        game_model.game.dispatch(payload=payload)

        self.game_data_access.save(model=game_model)
