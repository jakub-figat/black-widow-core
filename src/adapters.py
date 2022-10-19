from typing import Any, Optional

from socketio import Server


server = Server()


@server.event("dupisko")
def on_dupisko(session_id: str, data: dict[str, Any]):
    print(session_id, data)
