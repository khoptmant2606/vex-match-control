"""
VEX U 4-Channel Match Manager.
Coordinates the hierarchy: Match -> Team -> Player -> Controller -> Robot.
"""
from typing import Dict, Any
from common.states import (
    MatchState, RobotControlState, TeamRole, PlayerID, RobotID,
    ProgramStatus, ControlPermission
)
from common.config import AUTON_DURATION, DRIVER_DURATION, TEAM_CONFIG
from server.state_machine import MatchStateMachine, StateMachineError
from server.timer import MatchTimer
from server.safety import PlayerSafetyMonitor
from server.logger import server_logger

class VexUMatchManager:
    def __init__(self, broadcast_callback):
        self.broadcast_callback = broadcast_callback
        self.sm = MatchStateMachine()
        self.safety = PlayerSafetyMonitor()
        self.timer = MatchTimer(
            on_tick=self._handle_timer_tick,
            on_expire=self._handle_timer_expire
        )
        self.match_id = "VEX-U-PRACTICE-01"

        # 4-Channel Data Hierarchy Model
        self.channels: Dict[str, Dict[str, Any]] = {
            "RED-P1": {
                "team": "RED", "player_id": "RED-P1", "robot_id": "RED-1",
                "controller_id": "RED-C1", "connected": False, "controller_connected": False,
                "program": "None", "program_status": ProgramStatus.NOT_SELECTED,
                "robot_state": RobotControlState.DISABLED, "individually_disabled": False
            },
            "RED-P2": {
                "team": "RED", "player_id": "RED-P2", "robot_id": "RED-2",
                "controller_id": "RED-C2", "connected": False, "controller_connected": False,
                "program": "None", "program_status": ProgramStatus.NOT_SELECTED,
                "robot_state": RobotControlState.DISABLED, "individually_disabled": False
            },
            "BLUE-P1": {
                "team": "BLUE", "player_id": "BLUE-P1", "robot_id": "BLUE-1",
                "controller_id": "BLUE-C1", "connected": False, "controller_connected": False,
                "program": "None", "program_status": ProgramStatus.NOT_SELECTED,
                "robot_state": RobotControlState.DISABLED, "individually_disabled": False
            },
            "BLUE-P2": {
                "team": "BLUE", "player_id": "BLUE-P2", "robot_id": "BLUE-2",
                "controller_id": "BLUE-C2", "connected": False, "controller_connected": False,
                "program": "None", "program_status": ProgramStatus.NOT_SELECTED,
                "robot_state": RobotControlState.DISABLED, "individually_disabled": False
            }
        }

    def _handle_timer_tick(self, display: str, remaining: int):
        self.broadcast_callback()

    def _handle_timer_expire(self):
        cur = self.sm.current_state
        server_logger.log(f"TIMER EXPIRED in phase: {cur.value}")
        if cur == MatchState.AUTONOMOUS:
            self.execute_disable()
            server_logger.log("AUTONOMOUS PHASE COMPLETE (30s). TRANSITIONING TO DISABLED.")
        elif cur == MatchState.DRIVER_CONTROL:
            self.execute_match_end()
            server_logger.log("DRIVER CONTROL PHASE COMPLETE (90s). MATCH ENDED.")

    def set_player_connection(self, player_id: str, connected: bool):
        if player_id in self.channels:
            ch = self.channels[player_id]
            ch["connected"] = connected
            ch["controller_connected"] = connected
            if not connected:
                ch["robot_state"] = RobotControlState.DISABLED
                self.safety.purge(player_id)
                server_logger.log(f"SAFETY HAZARD: {player_id} disconnected! Assigned {ch['robot_id']} DISABLED.")
            else:
                self.safety.record_heartbeat(player_id)
                server_logger.log(f"AUTH CONNECT: {player_id} linked to {ch['robot_id']}.")
            self._update_robot_states()
            self.broadcast_callback()

    def update_player_program(self, player_id: str, program_name: str, status: ProgramStatus):
        if player_id in self.channels:
            ch = self.channels[player_id]
            ch["program"] = program_name
            ch["program_status"] = status
            server_logger.log(f"PROGRAM TELEMETRY [{player_id} -> {ch['robot_id']}]: '{program_name}' [{status.value}]")
            
            # Check if all 4 are ready
            if self.sm.current_state == MatchState.IDLE and self.is_ready_to_start():
                self.sm.transition_to(MatchState.READY)
            self._update_robot_states()
            self.broadcast_callback()

    def is_ready_to_start(self) -> bool:
        """Verifies all 4 players are connected and programs are prepared."""
        for pid, ch in self.channels.items():
            if not ch["connected"] or ch["program_status"] not in (ProgramStatus.READY, ProgramStatus.RUNNING):
                return False
        return True

    def toggle_individual_disable(self, robot_id: str):
        """Allows Game Master to selectively disable/enable a single robot."""
        for ch in self.channels.values():
            if ch["robot_id"] == robot_id:
                ch["individually_disabled"] = not ch["individually_disabled"]
                server_logger.log(f"ADMIN OVERRIDE: {robot_id} Individual Disable = {ch['individually_disabled']}")
                break
        self._update_robot_states()
        self.broadcast_callback()

    def _update_robot_states(self):
        """Calculates discrete authorization state for each of the 4 robots."""
        global_state = self.sm.current_state
        for pid, ch in self.channels.items():
            if not ch["connected"] or ch["individually_disabled"]:
                ch["robot_state"] = RobotControlState.DISABLED
            elif global_state == MatchState.EMERGENCY_STOP:
                ch["robot_state"] = RobotControlState.EMERGENCY_STOP
            elif global_state == MatchState.AUTONOMOUS:
                ch["robot_state"] = RobotControlState.AUTONOMOUS
            elif global_state == MatchState.DRIVER_CONTROL:
                ch["robot_state"] = RobotControlState.DRIVER_CONTROL
            else:
                ch["robot_state"] = RobotControlState.DISABLED

    # --- Game Master Match Controls ---
    def start_autonomous(self):
        self.sm.transition_to(MatchState.AUTONOMOUS)
        self.timer.start(AUTON_DURATION)
        server_logger.log("MATCH EVENT: 30-Second Autonomous Phase Started.")
        self._update_robot_states()
        self.broadcast_callback()

    def start_driver_control(self):
        if self.sm.current_state != MatchState.DISABLED:
            raise StateMachineError("Field must transition through DISABLED before Driver Control.")
        self.sm.transition_to(MatchState.DRIVER_CONTROL)
        self.timer.start(DRIVER_DURATION)
        server_logger.log("MATCH EVENT: 90-Second Driver Control Phase Started.")
        self._update_robot_states()
        self.broadcast_callback()

    def execute_disable(self):
        self.timer.pause()
        self.sm.transition_to(MatchState.DISABLED, force=(self.sm.current_state == MatchState.EMERGENCY_STOP))
        server_logger.log("MATCH EVENT: Field Globally Disabled.")
        self._update_robot_states()
        self.broadcast_callback()

    def execute_emergency_stop(self):
        self.timer.pause()
        self.sm.transition_to(MatchState.EMERGENCY_STOP)
        server_logger.log("CRITICAL: GLOBAL EMERGENCY STOP ACTIVATED.")
        self._update_robot_states()
        self.broadcast_callback()

    def execute_match_end(self):
        self.timer.pause()
        self.sm.transition_to(MatchState.MATCH_ENDED)
        server_logger.log("MATCH EVENT: Match Finished. All 4 robots disabled.")
        self._update_robot_states()
        self.broadcast_callback()

    def execute_reset(self):
        self.timer.reset(0)
        self.sm.transition_to(MatchState.IDLE, force=True)
        for ch in self.channels.values():
            ch["program_status"] = ProgramStatus.NOT_SELECTED
            ch["individually_disabled"] = False
        server_logger.log("MATCH EVENT: Full Match System Reset to IDLE.")
        self._update_robot_states()
        self.broadcast_callback()

    def get_permission(self, player_id: str) -> ControlPermission:
        ch = self.channels.get(player_id)
        if not ch or not ch["connected"] or ch["individually_disabled"]:
            return ControlPermission.BLOCKED
        if self.sm.current_state == MatchState.DRIVER_CONTROL:
            return ControlPermission.AUTHORIZED
        if self.sm.current_state == MatchState.AUTONOMOUS:
            return ControlPermission.BLOCKED  # Driver inputs locked out in Auton
        return ControlPermission.WAITING
    
    # Alias for backwards compatibility
MatchManager = VexUMatchManager