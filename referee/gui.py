"""
Enhanced VEX U Game Master Tactical Dashboard.
Features 4-channel telemetry, individual robot disable buttons, and large timing indicators.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class RefereeGUI:
    def __init__(self, root: tk.Tk, bridge_factory):
        self.root = root
        self.bridge_factory = bridge_factory
        self.bridge = None

        self.root.title("VEX U PRACTICE MATCH CONTROLLER // GAME MASTER DASHBOARD")
        self.root.geometry("1100x780")
        self.root.configure(bg="#070B13")

        self.font_title = ("Consolas", 15, "bold")
        self.font_clock = ("Consolas", 64, "bold")
        self.font_hdr = ("Consolas", 12, "bold")
        self.font_data = ("Consolas", 10)

        self._build_interface()

    def _build_interface(self):
        # 1. Top System Header
        top = tk.Frame(self.root, bg="#0D1424", padx=16, pady=10, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)

        tk.Label(top, text="VEX U TOURNAMENT // FIELD CONTROL OS", font=self.font_title, fg="#38BDF8", bg="#0D1424").pack(side=tk.LEFT)
        
        # Connect subframe
        conn_box = tk.Frame(top, bg="#0D1424")
        conn_box.pack(side=tk.RIGHT)
        tk.Label(conn_box, text="HOST:", font=self.font_data, fg="#94A3B8", bg="#0D1424").pack(side=tk.LEFT)
        self.entry_ip = tk.Entry(conn_box, font=self.font_data, bg="#1E2C4A", fg="#FFF", insertbackground="white", width=14)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack(side=tk.LEFT, padx=6)
        self.btn_connect = tk.Button(conn_box, text="CONNECT", font=("Consolas", 9, "bold"), bg="#0284C7", fg="white", command=self._on_connect, padx=10)
        self.btn_connect.pack(side=tk.LEFT)

        # 2. Center Stage Clock HUD
        hud = tk.Frame(self.root, bg="#040711", bd=2, relief=tk.SOLID, padx=20, pady=12)
        hud.pack(fill=tk.X, padx=20, pady=10)

        self.lbl_match_state = tk.Label(hud, text="FIELD STATE: IDLE", font=self.font_hdr, fg="#F59E0B", bg="#040711")
        self.lbl_match_state.pack()

        self.lbl_timer = tk.Label(hud, text="00:00", font=self.font_clock, fg="#F8FAFC", bg="#040711")
        self.lbl_timer.pack()

        self.lbl_ready_badge = tk.Label(hud, text="STATUS: WAITING FOR ALL 4 PLAYERS TO CONNECT & ARM", font=self.font_data, fg="#EF4444", bg="#040711")
        self.lbl_ready_badge.pack(pady=2)

        # 3. 4-Channel Grid (Red Team Left, Blue Team Right)
        grid_frame = tk.Frame(self.root, bg="#070B13", padx=20)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Red Column
        red_col = tk.LabelFrame(grid_frame, text=" RED ALLIANCE (2 PLAYERS / 2 ROBOTS) ", font=self.font_hdr, fg="#EF4444", bg="#0D1424", padx=12, pady=10)
        red_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.card_red_1 = self._create_robot_card(red_col, "RED-1", "RED-P1", "RED-C1")
        self.card_red_2 = self._create_robot_card(red_col, "RED-2", "RED-P2", "RED-C2")

        # Blue Column
        blue_col = tk.LabelFrame(grid_frame, text=" BLUE ALLIANCE (2 PLAYERS / 2 ROBOTS) ", font=self.font_hdr, fg="#3B82F6", bg="#0D1424", padx=12, pady=10)
        blue_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.card_blue_1 = self._create_robot_card(blue_col, "BLUE-1", "BLUE-P1", "BLUE-C1")
        self.card_blue_2 = self._create_robot_card(blue_col, "BLUE-2", "BLUE-P2", "BLUE-C2")

        # 4. Tactical Action Command Bank
        ctrls = tk.Frame(self.root, bg="#0D1424", padx=20, pady=12, bd=1, relief=tk.SOLID)
        ctrls.pack(fill=tk.X, padx=20, pady=10)

        row1 = tk.Frame(ctrls, bg="#0D1424")
        row1.pack(fill=tk.X, pady=3)

        self.btn_auton = tk.Button(row1, text="START AUTONOMOUS (30S)", font=self.font_hdr, bg="#D97706", fg="black", command=lambda: self._send_cmd("AUTONOMOUS"), height=2)
        self.btn_auton.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_driver = tk.Button(row1, text="DRIVER CONTROL (90S)", font=self.font_hdr, bg="#2563EB", fg="white", command=lambda: self._send_cmd("DRIVER"), height=2)
        self.btn_driver.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        row2 = tk.Frame(ctrls, bg="#0D1424")
        row2.pack(fill=tk.X, pady=3)

        self.btn_disable = tk.Button(row2, text="DISABLE ALL ROBOTS", font=self.font_hdr, bg="#334155", fg="white", command=lambda: self._send_cmd("DISABLE"), height=2)
        self.btn_disable.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_reset = tk.Button(row2, text="RESET MATCH", font=self.font_hdr, bg="#1E293B", fg="#94A3B8", command=self._confirm_reset, height=2)
        self.btn_reset.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # High-Impact Emergency Stop
        self.btn_estop = tk.Button(ctrls, text="⚠️ EMERGENCY STOP (OVERRIDE ALL 4 ROBOTS)", font=("Consolas", 15, "bold"), bg="#DC2626", fg="white", command=lambda: self._send_cmd("ESTOP"), height=2)
        self.btn_estop.pack(fill=tk.X, pady=(6, 0), padx=4)

    def _create_robot_card(self, parent, robot_id, player_id, ctrl_id):
        box = tk.Frame(parent, bg="#121C32", bd=1, relief=tk.SOLID, padx=10, pady=8)
        box.pack(fill=tk.X, pady=6)

        hdr_row = tk.Frame(box, bg="#121C32")
        hdr_row.pack(fill=tk.X)
        tk.Label(hdr_row, text=f"{robot_id}", font=("Consolas", 13, "bold"), fg="#FFF", bg="#121C32").pack(side=tk.LEFT)
        btn_indiv = tk.Button(hdr_row, text=f"DISABLE {robot_id}", font=("Consolas", 8, "bold"), bg="#475569", fg="#FFF", command=lambda: self._disable_single(robot_id))
        btn_indiv.pack(side=tk.RIGHT)

        lbl_player = tk.Label(box, text=f"Player: {player_id}  |  Ctrl: {ctrl_id}", font=self.font_data, fg="#94A3B8", bg="#121C32")
        lbl_player.pack(anchor="w")

        lbl_conn = tk.Label(box, text="Connection: DISCONNECTED ✗", font=self.font_data, fg="#EF4444", bg="#121C32")
        lbl_conn.pack(anchor="w")

        lbl_prog = tk.Label(box, text="Program: NOT_SELECTED", font=self.font_data, fg="#94A3B8", bg="#121C32")
        lbl_prog.pack(anchor="w")

        lbl_ctrl = tk.Label(box, text="Control Status: LOCKED / DISABLED", font=self.font_data, fg="#F59E0B", bg="#121C32")
        lbl_ctrl.pack(anchor="w")

        return {
            "box": box, "lbl_conn": lbl_conn, "lbl_prog": lbl_prog,
            "lbl_ctrl": lbl_ctrl, "btn_indiv": btn_indiv
        }

    def _on_connect(self):
        host = self.entry_ip.get().strip()
        self.bridge = self.bridge_factory(host, self.update_telemetry)
        self.btn_connect.config(state=tk.DISABLED, text="ACTIVE")

    def update_telemetry(self, data):
        self.lbl_timer.config(text=data.get("timer", "00:00"))
        st = data.get("field_state", "IDLE")
        self.lbl_match_state.config(text=f"FIELD STATE: {st}")

        all_ready = data.get("all_ready", False)
        if all_ready:
            self.lbl_ready_badge.config(text="MATCH READY: ALL 4 ROBOTS LINKED & ARMED ✓", fg="#10B981")
        else:
            self.lbl_ready_badge.config(text="STATUS: WAITING FOR ALL 4 PLAYERS TO CONNECT & ARM", fg="#EF4444")

        channels = data.get("channels", {})
        cards = {
            "RED-P1": self.card_red_1,
            "RED-P2": self.card_red_2,
            "BLUE-P1": self.card_blue_1,
            "BLUE-P2": self.card_blue_2
        }

        for pid, card in cards.items():
            ch = channels.get(pid, {})
            conn = ch.get("connected", False)
            card["lbl_conn"].config(
                text=f"Connection: {'ONLINE ✓' if conn else 'DISCONNECTED ✗'}",
                fg="#10B981" if conn else "#EF4444"
            )

            p_name = ch.get("program", "None")
            p_stat = ch.get("program_status", "NOT_SELECTED")
            card["lbl_prog"].config(text=f"Program: {p_name} [{p_stat}]")

            r_state = ch.get("robot_state", "DISABLED")
            indiv_dis = ch.get("individually_disabled", False)

            if indiv_dis:
                card["lbl_ctrl"].config(text="Control: INDIVIDUALLY DISABLED 🛑", fg="#EF4444")
                card["btn_indiv"].config(text=f"ENABLE {ch.get('robot_id')}", bg="#10B981")
            else:
                card["btn_indiv"].config(text=f"DISABLE {ch.get('robot_id')}", bg="#475569")
                if r_state == "DRIVER_CONTROL":
                    card["lbl_ctrl"].config(text="Control: AUTHORIZED (DRIVER ENABLED) ✓", fg="#10B981")
                elif r_state == "AUTONOMOUS":
                    card["lbl_ctrl"].config(text="Control: AUTONOMOUS ROUTINE (INPUTS BLOCKED)", fg="#D97706")
                elif r_state == "EMERGENCY_STOP":
                    card["lbl_ctrl"].config(text="Control: EMERGENCY STOPPED", fg="#EF4444")
                else:
                    card["lbl_ctrl"].config(text="Control: LOCKED / DISABLED", fg="#F59E0B")

    def _send_cmd(self, cmd: str):
        if self.bridge: self.bridge.send_admin_command(cmd)

    def _disable_single(self, robot_id: str):
        if self.bridge: self.bridge.send_individual_disable(robot_id)

    def _confirm_reset(self):
        if messagebox.askyesno("Confirm Reset", "Reset practice match to IDLE state?"):
            self._send_cmd("RESET")