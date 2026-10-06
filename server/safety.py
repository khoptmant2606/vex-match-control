"""
Per-player heartbeat monitor enforcing discrete containment:
If one player drops, only their assigned robot is safety-disabled.
"""
import time
from typing import Dict
from common.config import HEARTBEAT_TIMEOUT
from common.states import PlayerID

class PlayerSafetyMonitor:
    def __init__(self):
        self._last_heartbeat: Dict[str, float] = {}

    def record_heartbeat(self, player_id: str):
        self._last_heartbeat[player_id] = time.time()

    def check_timeouts(self) -> Dict[str, bool]:
        """Returns map of player_id -> is_alive."""
        now = time.time()
        status = {}
        for pid in ["RED-P1", "RED-P2", "BLUE-P1", "BLUE-P2"]:
            last = self._last_heartbeat.get(pid, 0)
            status[pid] = (now - last) <= HEARTBEAT_TIMEOUT
        return status

    def purge(self, player_id: str):
        if player_id in self._last_heartbeat:
            del self._last_heartbeat[player_id]