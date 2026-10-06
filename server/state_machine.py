"""
Strict authoritative match state machine with mathematical transition guards.
"""
from typing import Dict, Set
from common.states import MatchState
from server.logger import server_logger

class StateMachineError(Exception):
    pass

class MatchStateMachine:
    # Explicit mapping of permitted forward and reverse transitions
    VALID_TRANSITIONS: Dict[MatchState, Set[MatchState]] = {
        MatchState.IDLE: {MatchState.READY, MatchState.DISABLED, MatchState.EMERGENCY_STOP},
        MatchState.READY: {MatchState.PROGRAM_RUNNING, MatchState.DISABLED, MatchState.IDLE, MatchState.EMERGENCY_STOP},
        MatchState.PROGRAM_RUNNING: {MatchState.DISABLED, MatchState.EMERGENCY_STOP},
        MatchState.DISABLED: {MatchState.AUTONOMOUS, MatchState.DRIVER_CONTROL, MatchState.MATCH_ENDED, MatchState.READY, MatchState.IDLE, MatchState.EMERGENCY_STOP},
        MatchState.AUTONOMOUS: {MatchState.DISABLED, MatchState.EMERGENCY_STOP},
        MatchState.DRIVER_CONTROL: {MatchState.DISABLED, MatchState.MATCH_ENDED, MatchState.EMERGENCY_STOP},
        MatchState.MATCH_ENDED: {MatchState.DISABLED, MatchState.IDLE, MatchState.EMERGENCY_STOP},
        MatchState.EMERGENCY_STOP: {MatchState.IDLE, MatchState.DISABLED}  # Only manual reset allowed
    }

    def __init__(self):
        self._state: MatchState = MatchState.IDLE

    @property
    def current_state(self) -> MatchState:
        return self._state

    def transition_to(self, target: MatchState, force: bool = False) -> MatchState:
        if force:
            server_logger.log(f"FORCED STATE OVERRIDE: {self._state.value} -> {target.value}")
            self._state = target
            return self._state

        if target == MatchState.EMERGENCY_STOP:
            server_logger.log(f"CRITICAL SAFETY OVERRIDE: {self._state.value} -> EMERGENCY_STOP")
            self._state = target
            return self._state

        allowed = self.VALID_TRANSITIONS.get(self._state, set())
        if target not in allowed:
            err = f"ILLEGAL STATE TRANSITION: Attempted {self._state.value} -> {target.value}. Transition rejected."
            server_logger.log(err)
            raise StateMachineError(err)

        server_logger.log(f"STATE TRANSITION: {self._state.value} -> {target.value}")
        self._state = target
        return self._state