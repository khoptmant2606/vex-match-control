"""
JSON protocol serializer with strict server-side ownership validator.
"""
import json
import time
from typing import Any, Dict, Optional
from common.messages import MessageType
from common.states import PlayerID, RobotID, TeamRole
from common.config import TEAM_CONFIG

class ProtocolError(Exception):
    pass

class Protocol:
    @staticmethod
    def serialize(message_type: MessageType, payload: Optional[Dict[str, Any]] = None) -> str:
        data = {
            "type": message_type.value,
            "timestamp": time.time(),
            "payload": payload or {}
        }
        return json.dumps(data)

    @staticmethod
    def deserialize(raw_data: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_data)
            if "type" not in data or "timestamp" not in data:
                raise ProtocolError("Missing message headers.")
            data["type"] = MessageType(data["type"])
            return data
        except (json.JSONDecodeError, ValueError) as err:
            raise ProtocolError(f"Protocol parsing error: {err}") from err

    @staticmethod
    def validate_ownership(player_id_str: str, robot_id_str: str) -> bool:
        """Enforces that a player is strictly permitted to control ONLY their assigned robot."""
        allowed_robot = TEAM_CONFIG["MAPPINGS"].get(player_id_str)
        return allowed_robot == robot_id_str