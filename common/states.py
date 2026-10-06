"""
Authoritative state definitions for VEX U multi-player match architecture.
"""
from enum import Enum, unique

@unique
class MatchState(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    PROGRAM_RUNNING = "PROGRAM_RUNNING"
    DISABLED = "DISABLED"
    AUTONOMOUS = "AUTONOMOUS"
    DRIVER_CONTROL = "DRIVER_CONTROL"
    MATCH_ENDED = "MATCH_ENDED"
    EMERGENCY_STOP = "EMERGENCY_STOP"

@unique
class RobotControlState(str, Enum):
    DISABLED = "DISABLED"
    AUTONOMOUS = "AUTONOMOUS"
    DRIVER_CONTROL = "DRIVER_CONTROL"
    EMERGENCY_STOP = "EMERGENCY_STOP"

@unique
class TeamRole(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    REFEREE = "REFEREE"

@unique
class PlayerID(str, Enum):
    RED_P1 = "RED-P1"
    RED_P2 = "RED-P2"
    BLUE_P1 = "BLUE-P1"
    BLUE_P2 = "BLUE-P2"

@unique
class RobotID(str, Enum):
    RED_1 = "RED-1"
    RED_2 = "RED-2"
    BLUE_1 = "BLUE-1"
    BLUE_2 = "BLUE-2"

@unique
class ProgramStatus(str, Enum):
    NOT_SELECTED = "NOT_SELECTED"
    READY = "READY"
    RUNNING = "RUNNING"

@unique
class ControlPermission(str, Enum):
    WAITING = "WAITING"
    AUTHORIZED = "AUTHORIZED"
    BLOCKED = "BLOCKED"