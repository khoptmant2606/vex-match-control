a# VEX U Practice Match Control System

A high-reliability, local-network competition control system designed for **VEX U practice matches**. Built entirely in **pure Python** with an authoritative server state machine, real-time WebSocket communication, and multi-channel driver station controls.

---

## 📌 Executive Summary

Official VEX competition hardware uses a centralized Field Control System to manage match timing and enable/disable robot states. This project simulates that field-control environment for private team practice and scrimmage sessions across three computers on a local Wi-Fi or LAN network.

### The Golden Rule
> **PROGRAM RUNNING DOES NOT EQUAL ROBOT CONTROL ENABLED.**
> 
> A team may load and start its autonomous or teleop program, but all motor outputs remain locked and safe in a `DISABLED` state until the Game Master server explicitly authorizes the appropriate match phase.

---

## 🤖 VEX U 2-Team / 4-Robot Hierarchy

Following official VEX U Head-to-Head guidelines (two teams, two robots per team), this system provides four independent control channels:

LAPTOP 3
                GAME MASTER / REFEREE
                (Authoritative Server)
                          │
           ┌──────────────┴──────────────┐
      (Local Wi-Fi)                 (Local Wi-Fi)
           ▼                             ▼
       LAPTOP 1                      LAPTOP 2
     RED ALLIANCE                  BLUE ALLIANCE
 (Dual-Player Console)         (Dual-Player Console)
    ├── RED-P1 ──> RED-1          ├── BLUE-P1 ──> BLUE-1
    └── RED-P2 ──> RED-2          └── BLUE-P2 ──> BLUE-2

    ### Discrete Control Channels
* **RED ALLIANCE:**
  * **Player 1 (`RED-P1`):** Controls Robot 1 (`RED-1`) via Controller `RED-C1`
  * **Player 2 (`RED-P2`):** Controls Robot 2 (`RED-2`) via Controller `RED-C2`
* **BLUE ALLIANCE:**
  * **Player 1 (`BLUE-P1`):** Controls Robot 1 (`BLUE-1`) via Controller `BLUE-C1`
  * **Player 2 (`BLUE-P2`):** Controls Robot 2 (`BLUE-2`) via Controller `BLUE-C2`

---

## ⏱️ VEX U Competition Timing
* **Autonomous Period:** Exactly `30 Seconds` *(All driver inputs blocked)*
* **Field Review Transition:** `Automatic Disable` *(Referees verify scores)*
* **Driver Control Period:** Exactly `90 Seconds` (`1:30`)
* **Match End:** `Automatic Disable` *(All 4 robots cut simultaneously)*

---

## 🛡️ Key Safety & Security Principles

1. **Server-Side Authority Only:** Client laptops cannot alter the match state or enable their own robots. Any unauthorized request to enable driver control is rejected and logged.
2. **Server-Validated Ownership:** The server verifies `PLAYER ID + TEAM + ROBOT ID + MATCH ID` on every command. Cross-robot control (e.g., `RED-P1` attempting to drive `RED-2` or `BLUE-1`) is blocked at the network level.
3. **Discrete Disconnect Containment:** If one player loses connection, **only their assigned robot is safety-disabled**. The other three robots continue operating normally without match interruption.
4. **Individual Robot Disable:** The Game Master can selectively disable or re-enable an individual robot (e.g., `DISABLE RED-1`) for practice troubleshooting without halting the entire field.
5. **Immediate Emergency Stop (E-Stop):** Global emergency stop overrides all 4 robots immediately and locks the system until a deliberate manual reset is issued.

---

## 📊 Finite State Machine (FSM)

The central server enforces valid transitions and rejects illegal commands:
*(Emergency Stop is accessible at any time and overrides all states).*

---

## 📂 Project Structure

```text
vex_match_control/
├── common/
│   ├── config.py           # Network settings, VEX U timing (30s/90s), and mappings
│   ├── states.py           # Enums for MatchState, RobotControlState, PlayerID, RobotID
│   ├── messages.py         # JSON message types
│   └── protocol.py         # Serializer and strict ownership validation
├── server/
│   ├── main.py             # Authoritative server entry point
│   ├── match_manager.py    # 4-channel hierarchy coordinator and timer hooks
│   ├── state_machine.py    # Strict match state transition guards
│   ├── safety.py           # Per-player heartbeat monitoring
│   ├── websocket_server.py # Asynchronous WebSocket network handler
│   └── logger.py           # Persistent match event logger
├── referee/
│   ├── main.py             # Game Master GUI launcher
│   ├── gui.py              # Tactical 4-robot Game Master Console
│   └── controls.py         # WebSocket bridge for admin actions
├── team_client/
│   ├── alliance_gui.py     # Dual-player driver station GUI
│   ├── network.py          # WebSocket client with heartbeat support
│   └── program_manager.py  # Code slot selector and execution state tracker
├── robot/
│   ├── red/main.py         # VEX V5 Python compliant control loop for Red
│   └── blue/main.py        # VEX V5 Python compliant control loop for Blue
├── run_blue_team.py        # One-click launcher for Laptop 2 (Blue Alliance)
├── run_red_team.py         # One-click launcher for Laptop 1 (Red Alliance)
├── requirements.txt        # Python dependencies
└── README.md

pip install -r requirements.txt

# Terminal 1: Background Engine
python -m server.main

# Terminal 2: Game Master Console
python -m referee.main

# Terminal 3: Blue Alliance (Players 1 & 2)
python run_blue_team.py

# Terminal 4: Red Alliance (Players 1 & 2)
python run_red_team.py
