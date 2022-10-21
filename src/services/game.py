from typing import Any, Optional
from uuid import uuid4

from src.core.game import Game
from src.data_access.exceptions import DataAccessException, DoesNotExist
from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.schemas.game import GameModel
from src.schemas.lobby import LobbyModel
from src.schemas.user import UserModel


class GameService:
    def __init__(
        self, game_data_access: GameDataAccess, user_data_access: UserDataAccess, lobby_data_access: LobbyDataAccess
    ) -> None:
        self._game_data_access = game_data_access
        self._user_data_access = user_data_access
        self._lobby_data_access = lobby_data_access

    def create_lobby(self, user: UserModel, max_players: int = 3) -> LobbyModel:
        lobby = LobbyModel(lobby_id=str(uuid4()), users=[user.email], max_players=max_players)
        self._lobby_data_access.save(model=lobby)

        user.lobbies_ids.append(lobby.lobby_id)
        self._user_data_access.save(model=user)

        return lobby

    def add_user_to_lobby(self, lobby_id: str, user: UserModel) -> Optional[GameModel]:
        lobby_key = {"pk": f"games#lobby#{lobby_id}", "sk": f"games#lobby#{lobby_id}"}
        lobby = self._lobby_data_access.get(**lobby_key)
        if lobby is None:
            raise DoesNotExist(f"Lobby with id {lobby_id} does not exist.")

        if len(lobby.users) + 1 == lobby.max_players:  # lobby will be full, we can start the game
            users = [
                self._user_data_access.get(pk=f"games#user#{email}", sk=f"games#user#{email}") for email in lobby.users
            ]
            game_id = str(uuid4())
            for user_ in users:
                user_.lobbies_ids.remove(lobby_id)

            for user_ in users + [user]:
                user_.games_ids.append(game_id)

            self._user_data_access.bulk_save(models=users + [user])
            self._lobby_data_access.delete(**lobby_key)

            game = GameModel(
                game_id=game_id, game=Game.start_game(users=[user.email for user in users] + [user.email])
            )
            self._game_data_access.save(model=game)

            return game

        lobby.users.append(user.email)
        self._lobby_data_access.save(model=lobby)

        user.lobbies_ids.append(lobby.lobby_id)
        self._user_data_access.save(model=user)

    def remove_user_from_lobby(self, lobby_id: str, user: UserModel) -> None:
        lobby = self._lobby_data_access.get(pk=f"games#lobby#{lobby_id}", sk=f"games#lobby#{lobby_id}")
        if lobby is None:
            raise DoesNotExist(f"Lobby with id {lobby_id} does not exist.")

        if user.email not in lobby.users:
            raise DataAccessException(f"User {user.email} not found in lobby {lobby.lobby_id}")

        lobby.users.remove(user.email)
        self._lobby_data_access.save(model=lobby)

        user.lobbies_ids.remove(lobby_id)
        self._user_data_access.save(model=user)

    # TODO: tests and game end, exception handling
    def dispatch_game_action(self, game_id: str, user: UserModel, payload: dict[str, Any]) -> None:
        game_model = self._game_data_access.get(pk=f"games#{game_id}", sk=f"games#{game_id}")
        if game_model is None:
            raise DoesNotExist(f"Game with id {game_id} does not exist")
        payload = game_model.game.current_step.payload_class(**payload, user=user.email)
        game_model.game.dispatch(payload=payload)

        self._game_data_access.save(model=game_model)
