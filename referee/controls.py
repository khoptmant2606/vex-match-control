"""
Client bridge for Referee commands dispatching to the match server.
"""
import asyncio
import websockets
from common.messages import MessageType
from common.protocol import Protocol
from common.states import TeamRole

class RefereeBridge:
    def __init__(self, loop, on_state_update):
        self.loop = loop
        self.on_state_update = on_state_update
        self.ws = None

    async def connect(self, host: str, port: int):
        uri = f"ws://{host}:{port}"
        self.ws = await websockets.connect(uri)
        # Register as Referee
        await self.ws.send(Protocol.serialize(MessageType.HELLO, {"role": TeamRole.REFEREE.value}))
        asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = Protocol.deserialize(raw)
                if msg["type"] == MessageType.FIELD_STATE:
                    self.on_state_update(msg["payload"])
                elif msg["type"] == MessageType.HEARTBEAT:
                    await self.ws.send(Protocol.serialize(MessageType.HEARTBEAT_ACK, {}))
        except Exception:
            pass

    def send_admin_command(self, cmd: str):
        if self.ws and self.ws.open:
            payload = Protocol.serialize(MessageType.ADMIN_COMMAND, {"command": cmd})
            asyncio.run_coroutine_threadsafe(self.ws.send(payload), self.loop)