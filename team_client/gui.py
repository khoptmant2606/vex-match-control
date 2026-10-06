"""
Enhanced VEX U Player Control Interface.
Provides individual player-to-robot telemetry and controller pairing verification.
"""
import tkinter as tk
from tkinter import ttk
from common.states import ProgramStatus
from team_client.program_manager import ProgramManager

class TeamClientGUI:
    def __init__(self, root: tk.Tk, role: str, player_id: str, robot_id: str, bridge_factory):
        self.root = root
        self.role = role
        self.player_id = player_id
        self.robot_id = robot_id
        self.bridge_factory = bridge_factory
        self.pm = ProgramManager()
        self.net = None

        self.color_accent = "#EF4444" if self.role == "RED" else "#3B82F6"
        self.root.title(f"VEX U Player Station // {self.player_id} -> {self.robot_id}")
        self.root.geometry("640x620")
        self.root.configure(bg="#070B13")

        self._build_ui()

    def _build_ui(self):
        # Header Box
        hdr = tk.Frame(self.root, bg="#0D1424", padx=16, pady=12, bd=1, relief=tk.SOLID)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"{self.player_id} STATION", font=("Consolas", 18, "bold"), fg=self.color_accent, bg="#0D1424").pack(side=tk.LEFT)
        self.lbl_conn = tk.Label(hdr, text="DISCONNECTED ✗", font=("Consolas", 12, "bold"), fg="#EF4444", bg="#0D1424")
        self.lbl_conn.pack(side=tk.RIGHT)

        # Ownership Card
        owner_frame = tk.Frame(self.root, bg="#121C32", padx=15, pady=8)
        owner_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(owner_frame, text=f"ASSIGNED ROBOT: {self.robot_id}  |  ALLIANCE: {self.role}", font=("Consolas", 11, "bold"), fg="#FFF", bg="#121C32").pack()

        # Connect bar
        conn_frame = tk.Frame(self.root, bg="#070B13", padx=20, pady=4)
        conn_frame.pack(fill=tk.X)
        tk.Label(conn_frame, text="Game Master IP:", font=("Consolas", 10), fg="#94A3B8", bg="#070B13").pack(side=tk.LEFT)
        self.entry_ip = tk.Entry(conn_frame, font=("Consolas", 10), bg="#1E2C4A", fg="#FFF", insertbackground="white", width=14)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack(side=tk.LEFT, padx=6)
        self.btn_connect = tk.Button(conn_frame, text="CONNECT", font=("Consolas", 9, "bold"), bg="#0284C7", fg="white", command=self._on_connect)
        self.btn_connect.pack(side=tk.LEFT)

        # Field Status HUD
        hud = tk.Frame(self.root, bg="#040711", bd=2, relief=tk.SOLID, padx=15, pady=12)
        hud.pack(fill=tk.X, padx=20, pady=8)
        self.lbl_timer = tk.Label(hud, text="00:00", font=("Consolas", 44, "bold"), fg="#F8FAFC", bg="#040711")
        self.lbl_timer.pack()
        self.lbl_field = tk.Label(hud, text="FIELD: DISABLED", font=("Consolas", 13, "bold"), fg="#F59E0B", bg="#040711")
        self.lbl_field.pack()

        # Authorization State Box
        self.auth_box = tk.Frame(self.root, bg="#1E293B", padx=12, pady=12)
        self.auth_box.pack(fill=tk.X, padx=20, pady=6)
        self.lbl_permission = tk.Label(self.auth_box, text="CONTROL STATUS: WAITING FOR REFEREE", font=("Consolas", 12, "bold"), fg="#F59E0B", bg="#1E293B")
        self.lbl_permission.pack()

        # Independent Program Selection
        p_frame = tk.LabelFrame(self.root, text=f" {self.robot_id} PROGRAM SELECTION ", font=("Consolas", 11, "bold"), fg="#38BDF8", bg="#0D1424", padx=15, pady=12)
        p_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        self.cb_prog = ttk.Combobox(p_frame, values=self.pm.AVAILABLE_PROGRAMS, font=("Consolas", 11), state="readonly")
        self.cb_prog.set(self.pm.AVAILABLE_PROGRAMS[0])
        self.cb_prog.pack(fill=tk.X, pady=6)

        btn_row = tk.Frame(p_frame, bg="#0D1424")
        btn_row.pack(fill=tk.X, pady=6)

        self.btn_select = tk.Button(btn_row, text="1. SELECT PROGRAM", font=("Consolas", 10, "bold"), bg="#334155", fg="white", command=self._on_select_prog, width=17)
        self.btn_select.pack(side=tk.LEFT, padx=3)

        self.btn_run = tk.Button(btn_row, text="2. RUN PROGRAM", font=("Consolas", 10, "bold"), bg="#0284C7", fg="white", command=self._on_run_prog, width=17)
        self.btn_run.pack(side=tk.RIGHT, padx=3)

        self.lbl_prog_status = tk.Label(p_frame, text="Selected: None | Status: NOT_SELECTED", font=("Consolas", 10), fg="#94A3B8", bg="#0D1424")
        self.lbl_prog_status.pack(pady=6)

        rule = tk.Label(p_frame, text="* PROGRAM RUNNING DOES NOT GRANT DRIVER CONTROL\nROBOT REMAINS SAFE & DISABLED UNTIL AUTHORIZED BY REFEREE", font=("Consolas", 8, "italic"), fg="#64748B", bg="#0D1424")
        rule.pack()

    def _on_connect(self):
        host = self.entry_ip.get().strip()
        self.net = self.bridge_factory(host, self._on_state_update, self._on_conn_change)
        self.btn_connect.config(state=tk.DISABLED, text="ACTIVE")

    def _on_conn_change(self, is_online: bool):
        if is_online:
            self.lbl_conn.config(text="ONLINE ✓", fg="#10B981")
        else:
            self.lbl_conn.config(text="DISCONNECTED ✗", fg="#EF4444")
            self.btn_connect.config(state=tk.NORMAL, text="CONNECT")
            self.lbl_permission.config(text="SAFETY LOCKOUT: DISCONNECTED", fg="#EF4444")

    def _on_select_prog(self):
        chosen = self.cb_prog.get()
        self.pm.select(chosen)
        self.lbl_prog_status.config(text=f"Selected: {chosen} | Status: READY")
        if self.net:
            self.net.send_program_update(chosen, ProgramStatus.READY)

    def _on_run_prog(self):
        if self.pm.status != ProgramStatus.READY: return
        self.pm.start_running()
        self.lbl_prog_status.config(text=f"Selected: {self.pm.selected_program} | Status: RUNNING (STANDBY)")
        if self.net:
            self.net.send_program_update(self.pm.selected_program, ProgramStatus.RUNNING)

    def _on_state_update(self, data):
        self.lbl_timer.config(text=data.get("timer", "00:00"))
        f_state = data.get("field_state", "DISABLED")
        self.lbl_field.config(text=f"FIELD: {f_state}")

        ch = data.get("channels", {}).get(self.player_id, {})
        r_state = ch.get("robot_state", "DISABLED")
        indiv = ch.get("individually_disabled", False)

        if indiv:
            self.lbl_permission.config(text="ROBOT INDIVIDUALLY DISABLED BY GAME MASTER 🛑", fg="#EF4444")
            self.auth_box.config(bg="#3B0707")
        elif r_state == "DRIVER_CONTROL":
            self.lbl_permission.config(text=f"CONTROL AUTHORIZED: {self.robot_id} DRIVER ACTIVE ✓", fg="#10B981")
            self.auth_box.config(bg="#022C22")
        elif r_state == "AUTONOMOUS":
            self.lbl_permission.config(text=f"AUTONOMOUS ACTIVE: {self.robot_id} PRE-PROGRAMMED (INPUTS BLOCKED)", fg="#D97706")
            self.auth_box.config(bg="#2E1C03")
        elif r_state == "EMERGENCY_STOP":
            self.lbl_permission.config(text="EMERGENCY STOP (ALL CEASED)", fg="#EF4444")
            self.auth_box.config(bg="#3B0707")
        else:
            self.lbl_permission.config(text=f"STANDBY: {self.robot_id} DISABLED (WAITING FOR REFEREE)", fg="#F59E0B")
            self.auth_box.config(bg="#1E293B")