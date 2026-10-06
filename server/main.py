"""
Primary entry point for the authoritative Game Master server.
"""
import asyncio
from server.match_manager import VexUMatchManager
from server.websocket_server import WebSocketServer
from server.logger import server_logger

def main():
    server_logger.log("Starting VEX U Practice Match Controller Server Engine...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    ws_server = None

    def trigger_broadcast():
        if ws_server:
            asyncio.run_coroutine_threadsafe(ws_server.broadcast_state(), loop)

    manager = VexUMatchManager(broadcast_callback=trigger_broadcast)
    ws_server = WebSocketServer(manager)

    loop.run_until_complete(ws_server.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server_logger.log("Server shutting down cleanly...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()