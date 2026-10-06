"""
Application launcher for the Game Master GUI.
"""
import asyncio
import threading
import tkinter as tk
import websockets
from referee.controls import RefereeBridge
from referee.gui import RefereeGUI
from common.config import SERVER_PORT

def main():
    root = tk.Tk()
    loop = asyncio.new_event_loop()

    def run_async_loop(l):
        asyncio.set_event_loop(l)
        l.run_forever()

    threading.Thread(target=run_async_loop, args=(loop,), daemon=True).start()

    def bridge_factory(host, update_cb):
        b = RefereeBridge(loop, update_cb)
        asyncio.run_coroutine_threadsafe(b.connect(host, SERVER_PORT), loop)
        return b

    app = RefereeGUI(root, bridge_factory)
    root.mainloop()

if __name__ == "__main__":
    main()