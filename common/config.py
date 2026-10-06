"""
VEX U Match and Hierarchy Configurations.
"""
import os

# Server Networking
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765

# Official VEX U Head-to-Head Timing
AUTON_DURATION = 30     # 30 seconds Autonomous
DRIVER_DURATION = 90    # 90 seconds Driver Control

# Heartbeat & Safety
HEARTBEAT_INTERVAL = 1.0
HEARTBEAT_TIMEOUT = 3.0

# Extensible Hierarchy Data Configuration
TEAM_CONFIG = {
    "TEAMS": ["RED", "BLUE"],
    "PLAYERS_PER_TEAM": 2,
    "ROBOTS_PER_TEAM": 2,
    "MAPPINGS": {
        "RED-P1": "RED-1",
        "RED-P2": "RED-2",
        "BLUE-P1": "BLUE-1",
        "BLUE-P2": "BLUE-2"
    }
}

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)