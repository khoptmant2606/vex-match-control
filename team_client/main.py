"""
Team client entry point accepting CLI parameters:
python -m team_client.main --role [RED|BLUE] --player [P1|P2]
"""
import argparse
import asyncio
import threading
import tkinter as tk
from common.config import SERVER_PORT, TEAM_CONFIG
from team_client.network import TeamNetworkClient
from team_client.gui import TeamClientGUI

def main():
    parser = argparse.ArgumentParser(description="VEX U Player Control Client")
    parser.add_argument("--role", choices=["RED", "BLUE"], default="RED", help="Alliance color")
    parser.add_argument("--player", choices=["P1", "P2"], default="P1", help="Player number")
    args = parser.parse_args()

    player_id = f"{args.role.upper()}-{args.player.upper()}"
    robot_id = TEAM_CONFIG["MAPPINGS"][player_id]

    root = tk.Tk()
    loop = asyncio.new_event_loop()

    def run_loop(l):
        asyncio.set_event_loop(l)
        l.run_forever()

    threading.Thread(target=run_loop, args=(loop,), daemon=True).start()

    def bridge_factory(host, on_state, on_conn):
        client = TeamNetworkClient(player_id, loop, on_state, on_conn)
        asyncio.run_coroutine_threadsafe(client.connect(host, SERVER_PORT), loop)
        return client

    app = TeamClientGUI(root, args.role.upper(), player_id, robot_id, bridge_factory)
    root.mainloop()

if __name__ == "__main__":
    main()