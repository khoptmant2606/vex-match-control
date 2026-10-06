import os
import sys
import asyncio
import threading
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.config import SERVER_PORT
from team_client.network import TeamNetworkClient
from team_client.alliance_gui import AllianceStationGUI

def main():
    root = tk.Tk()
    loop = asyncio.new_event_loop()

    def run_loop(l):
        asyncio.set_event_loop(l)
        l.run_forever()

    threading.Thread(target=run_loop, args=(loop,), daemon=True).start()

    def bridge_factory(player_id, host, on_state, on_conn):
        client = TeamNetworkClient(player_id, loop, on_state, on_conn)
        asyncio.run_coroutine_threadsafe(client.connect(host, SERVER_PORT), loop)
        return client

    # Launch dedicated RED Alliance GUI
    app = AllianceStationGUI(root, team_color="RED", bridge_factory=bridge_factory)
    root.mainloop()

if __name__ == "__main__":
    main()