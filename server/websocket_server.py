"""
Asynchronous server enforcing strict player ownership and individual heartbeat isolation.
"""
import asyncio
import websockets
from typing import Dict, Optional
from common.config import SERVER_HOST, SERVER_PORT, HEARTBEAT_INTERVAL
from common.messages import MessageType
from common.states import TeamRole
from common.protocol import Protocol
from server.match_manager import VexUMatchManager
from server.logger import server_logger

class WebSocketServer:
    def __init__(self, manager: VexUMatchManager):
        self.manager = manager
        self.clients: Dict[websockets.WebSocketServerProtocol, Optional[str]] = {}
        self._server = None

    async def broadcast_state(self):
        if not self.clients:
            return
        payload = {
            "match_id": self.manager.match_id,
            "field_state": self.manager.sm.current_state.value,
            "timer": self.manager.timer.display_str,
            "channels": self.manager.channels,
            "all_ready": self.manager.is_ready_to_start()
        }
        msg = Protocol.serialize(MessageType.FIELD_STATE, payload)
        tasks = [client.send(msg) for client in self.clients.keys()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol):
        self.clients[websocket] = None
        server_logger.log(f"Socket opened: {websocket.remote_address}")
        try:
            async for raw in websocket:
                await self._process_message(websocket, raw)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            player_id = self.clients.pop(websocket, None)
            if player_id and player_id in self.manager.channels:
                self.manager.set_player_connection(player_id, False)
            server_logger.log(f"Socket disconnected for: {player_id}")
            await self.broadcast_state()

    async def _process_message(self, ws: websockets.WebSocketServerProtocol, raw: str):
        try:
            msg = Protocol.deserialize(raw)
            m_type = msg["type"]
            payload = msg.get("payload", {})

            # 1. Registration
            if m_type == MessageType.HELLO:
                role_str = payload.get("role")
                if role_str == TeamRole.REFEREE.value:
                    self.clients[ws] = "REFEREE"
                    server_logger.log("Game Master connected.")
                elif role_str in self.manager.channels:
                    self.clients[ws] = role_str
                    self.manager.set_player_connection(role_str, True)

                await ws.send(Protocol.serialize(MessageType.WELCOME, {"status": "ACK"}))
                await self.broadcast_state()

            # 2. Heartbeat Acknowledgement
            elif m_type == MessageType.HEARTBEAT_ACK:
                pid = self.clients.get(ws)
                if pid and pid in self.manager.channels:
                    self.manager.safety.record_heartbeat(pid)

            # 3. Program Registration
            elif m_type in (MessageType.PROGRAM_SELECTED, MessageType.PROGRAM_READY, MessageType.PROGRAM_STARTED):
                pid = self.clients.get(ws)
                if pid and pid in self.manager.channels:
                    p_name = payload.get("program", "Unknown")
                    status = payload.get("status")
                    self.manager.update_player_program(pid, p_name, status)

            # 4. Strict Ownership Guard for Robot Control Commands
            elif m_type == MessageType.ROBOT_COMMAND:
                pid = self.clients.get(ws)
                target_robot = payload.get("robot_id")
                
                # REJECT cross-control attempts on server side
                if not Protocol.validate_ownership(pid, target_robot):
                    server_logger.log(f"SECURITY BREACH: {pid} attempted unauthorized control of {target_robot}! REJECTED.")
                    await ws.send(Protocol.serialize(MessageType.ERROR, {"error": "Ownership mismatch. Unauthorized."}))
                    return

                # Check if authorized
                if self.manager.get_permission(pid).value != "AUTHORIZED":
                    return # Blocked or Waiting

            # 5. Game Master Admin Directives
            elif m_type == MessageType.ADMIN_COMMAND:
                if self.clients.get(ws) == "REFEREE":
                    cmd = payload.get("command")
                    if cmd == "AUTONOMOUS": self.manager.start_autonomous()
                    elif cmd == "DRIVER": self.manager.start_driver_control()
                    elif cmd == "DISABLE": self.manager.execute_disable()
                    elif cmd == "ESTOP": self.manager.execute_emergency_stop()
                    elif cmd == "RESET": self.manager.execute_reset()
                    elif cmd == "INDIVIDUAL_DISABLE":
                        target = payload.get("robot_id")
                        self.manager.toggle_individual_disable(target)
                else:
                    server_logger.log("UNAUTHORIZED ADMIN ATTEMPT DETECTED.")

        except Exception as e:
            server_logger.log(f"Protocol Error: {e}")

    async def heartbeat_sentinel(self):
        """Monitors each player independently. Dropping 1 player does NOT disconnect others."""
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            timeouts = self.manager.safety.check_timeouts()
            for pid, is_alive in timeouts.items():
                if not is_alive and self.manager.channels[pid]["connected"]:
                    server_logger.log(f"HEARTBEAT LOST for {pid}. Disabling only assigned robot.")
                    self.manager.set_player_connection(pid, False)

            if self.clients:
                msg = Protocol.serialize(MessageType.HEARTBEAT, {})
                tasks = [c.send(msg) for c in self.clients.keys()]
                await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self):
        self._server = await websockets.serve(self.handle_client, SERVER_HOST, SERVER_PORT)
        server_logger.log(f"VEX U Master Server online on {SERVER_HOST}:{SERVER_PORT}")
        asyncio.create_task(self.heartbeat_sentinel())