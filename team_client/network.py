"""
Network handler for Team Clients communicating with the central server.
"""
import asyncio
import websockets
from typing import Callable
from common.messages import MessageType
from common.states import TeamRole, ProgramStatus
from common.protocol import Protocol

class TeamNetworkClient:
    def __init__(self, role: TeamRole, loop: asyncio.AbstractEventLoop, on_state_update: Callable, on_connect_change: Callable):
        self.role = role
        self.loop = loop
        self.on_state_update = on_state_update
        self.on_connect_change = on_connect_change
        self.ws = None

    async def connect(self, host: str, port: int):
        uri = f"ws://{host}:{port}"
        try:
            self.ws = await websockets.connect(uri)
            self.on_connect_change(True)
            # Register Alliance Role
            await self.ws.send(Protocol.serialize(MessageType.HELLO, {"role": self.role.value}))
            asyncio.create_task(self._listen())
        except Exception:
            self.on_connect_change(False)

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = Protocol.deserialize(raw)
                m_type = msg["type"]
                payload = msg.get("payload", {})

                if m_type == MessageType.FIELD_STATE:
                    self.on_state_update(payload)
                elif m_type == MessageType.HEARTBEAT:
                    await self.ws.send(Protocol.serialize(MessageType.HEARTBEAT_ACK, {}))
        except Exception:
            self.on_connect_change(False)
        finally:
            self.on_connect_change(False)

    def send_program_update(self, program: str, status: ProgramStatus):
        if self.ws and self.ws.open:
            msg = Protocol.serialize(MessageType.PROGRAM_READY, {
                "program": program,
                "status": status.value
            })
            asyncio.run_coroutine_threadsafe(self.ws.send(msg), self.loop)