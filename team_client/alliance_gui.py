"""
Dual-Player Alliance Station GUI for Laptop 1 (RED) and Laptop 2 (BLUE).
Displays Player 1 and Player 2 side-by-side on the alliance laptop screen.
"""
import tkinter as tk
from tkinter import ttk
from common.states import ProgramStatus
from team_client.program_manager import ProgramManager

class AllianceStationGUI:
    def __init__(self, root: tk.Tk, team_color: str, bridge_factory):
        self.root = root
        self.team_color = team_color.upper()  # "BLUE" or "RED"
        self.bridge_factory = bridge_factory

        # IDs
        self.p1_id = f"{self.team_color}-P1"
        self.p2_id = f"{self.team_color}-P2"
        self.r1_id = f"{self.team_color}-1"
        self.r2_id = f"{self.team_color}-2"

        # Independent Program Managers for P1 and P2
        self.pm_p1 = ProgramManager()
        self.pm_p2 = ProgramManager()

        # Network bridges
        self.net_p1 = None
        self.net_p2 = None

        # Theme Colors
        self.theme_accent = "#3B82F6" if self.team_color == "BLUE" else "#EF4444"
        self.theme_bg = "#070B13"
        self.panel_bg = "#0D1424"
        self.card_bg = "#121C32"

        self.root.title(f"VEX U {self.team_color} ALLIANCE STATION // DRIVER CONSOLE")
        self.root.geometry("1020x680")
        self.root.configure(bg=self.theme_bg)

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, bg=self.panel_bg, padx=18, pady=12, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)

        tk.Label(top, text=f"{self.team_color} ALLIANCE DRIVER STATION", font=("Consolas", 18, "bold"), fg=self.theme_accent, bg=self.panel_bg).pack(side=tk.LEFT)

        conn_box = tk.Frame(top, bg=self.panel_bg)
        conn_box.pack(side=tk.RIGHT)
        tk.Label(conn_box, text="Game Master IP:", font=("Consolas", 10), fg="#94A3B8", bg=self.panel_bg).pack(side=tk.LEFT)
        self.entry_ip = tk.Entry(conn_box, font=("Consolas", 10), bg="#1E2C4A", fg="#FFF", insertbackground="white", width=14)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack(side=tk.LEFT, padx=6)
        
        self.btn_connect = tk.Button(conn_box, text="CONNECT BOTH PLAYERS", font=("Consolas", 9, "bold"), bg="#0284C7", fg="white", command=self._on_connect, padx=10)
        self.btn_connect.pack(side=tk.LEFT)

        self.lbl_overall_conn = tk.Label(conn_box, text="DISCONNECTED ✗", font=("Consolas", 10, "bold"), fg="#EF4444", bg=self.panel_bg)
        self.lbl_overall_conn.pack(side=tk.LEFT, padx=(10, 0))

        hud = tk.Frame(self.root, bg="#040711", bd=2, relief=tk.SOLID, padx=20, pady=12)
        hud.pack(fill=tk.X, padx=20, pady=10)

        self.lbl_field_state = tk.Label(hud, text="FIELD STATE: DISABLED", font=("Consolas", 14, "bold"), fg="#F59E0B", bg="#040711")
        self.lbl_field_state.pack()

        self.lbl_timer = tk.Label(hud, text="00:00", font=("Consolas", 56, "bold"), fg="#F8FAFC", bg="#040711")
        self.lbl_timer.pack()

        self.lbl_safety_notice = tk.Label(hud, text="* PROGRAM RUNNING DOES NOT GRANT DRIVER CONTROL — ROBOTS LOCKED UNTIL AUTHORIZED", font=("Consolas", 9, "italic"), fg="#64748B", bg="#040711")
        self.lbl_safety_notice.pack()

        grid = tk.Frame(self.root, bg=self.theme_bg, padx=20)
        grid.pack(fill=tk.BOTH, expand=True, pady=6)

        self.p1_widgets = self._create_player_column(grid, tk.LEFT, self.p1_id, self.r1_id, f"{self.team_color}-C1", self.pm_p1, player_num=1)
        self.p2_widgets = self._create_player_column(grid, tk.RIGHT, self.p2_id, self.r2_id, f"{self.team_color}-C2", self.pm_p2, player_num=2)

    def _create_player_column(self, parent, side, player_id, robot_id, ctrl_id, pm, player_num):
        frame = tk.LabelFrame(parent, text=f" PLAYER {player_num} ({player_id}) ", font=("Consolas", 12, "bold"), fg=self.theme_accent, bg=self.panel_bg, padx=14, pady=12)
        frame.pack(side=side, fill=tk.BOTH, expand=True, padx=6)

        tk.Label(frame, text=f"ASSIGNED ROBOT: {robot_id}   |   CONTROLLER: {ctrl_id}", font=("Consolas", 10, "bold"), fg="#E2E8F0", bg=self.panel_bg).pack(anchor="w", pady=(0, 4))
        
        lbl_status = tk.Label(frame, text="CONNECTION: STANDBY ⚪", font=("Consolas", 10), fg="#94A3B8", bg=self.panel_bg)
        lbl_status.pack(anchor="w", pady=(0, 8))

        p_box = tk.LabelFrame(frame, text=f" {robot_id} CODE ROUTINE ", font=("Consolas", 10, "bold"), fg="#38BDF8", bg=self.card_bg, padx=10, pady=10)
        p_box.pack(fill=tk.X, pady=6)

        cb = ttk.Combobox(p_box, values=pm.AVAILABLE_PROGRAMS, font=("Consolas", 10), state="readonly")
        cb.set(pm.AVAILABLE_PROGRAMS[0])
        cb.pack(fill=tk.X, pady=4)

        b_row = tk.Frame(p_box, bg=self.card_bg)
        b_row.pack(fill=tk.X, pady=6)

        btn_sel = tk.Button(b_row, text="1. SELECT", font=("Consolas", 9, "bold"), bg="#334155", fg="white", command=lambda: self._select_program(player_num, cb.get()), width=12)
        btn_sel.pack(side=tk.LEFT, padx=3)

        btn_run = tk.Button(b_row, text="2. RUN PROGRAM", font=("Consolas", 9, "bold"), bg="#0284C7", fg="white", command=lambda: self._run_program(player_num), width=14)
        btn_run.pack(side=tk.RIGHT, padx=3)

        lbl_prog_stat = tk.Label(p_box, text="Selected: None | Status: NOT_SELECTED", font=("Consolas", 9), fg="#94A3B8", bg=self.card_bg)
        lbl_prog_stat.pack(pady=4)

        auth_box = tk.Frame(frame, bg="#1E293B", padx=10, pady=12, bd=1, relief=tk.SOLID)
        auth_box.pack(fill=tk.X, pady=(10, 0))

        lbl_perm = tk.Label(auth_box, text=f"{robot_id} CONTROL: WAITING FOR REFEREE", font=("Consolas", 11, "bold"), fg="#F59E0B", bg="#1E293B")
        lbl_perm.pack()

        return {
            "lbl_status": lbl_status, "cb": cb, "lbl_prog_stat": lbl_prog_stat,
            "auth_box": auth_box, "lbl_perm": lbl_perm
        }

    def _on_connect(self):
        host = self.entry_ip.get().strip()
        self.btn_connect.config(state=tk.DISABLED, text="LINKING...")
        self.net_p1 = self.bridge_factory(self.p1_id, host, self._on_state_update, lambda c: self._on_player_conn(1, c))
        self.net_p2 = self.bridge_factory(self.p2_id, host, self._on_state_update, lambda c: self._on_player_conn(2, c))

    def _on_player_conn(self, player_num, is_online):
        w = self.p1_widgets if player_num == 1 else self.p2_widgets
        pid = self.p1_id if player_num == 1 else self.p2_id
        if is_online:
            w["lbl_status"].config(text=f"{pid} ONLINE ✓ (ARMED)", fg="#10B981")
            self.lbl_overall_conn.config(text="ALLIANCE ONLINE ✓", fg="#10B981")
            self.btn_connect.config(text="LINK ACTIVE")
        else:
            w["lbl_status"].config(text=f"{pid} DISCONNECTED ✗", fg="#EF4444")

    def _select_program(self, player_num, chosen):
        pm = self.pm_p1 if player_num == 1 else self.pm_p2
        net = self.net_p1 if player_num == 1 else self.net_p2
        w = self.p1_widgets if player_num == 1 else self.p2_widgets
        pm.select(chosen)
        w["lbl_prog_stat"].config(text=f"Selected: {chosen} | Status: READY")
        if net: net.send_program_update(chosen, ProgramStatus.READY)

    def _run_program(self, player_num):
        pm = self.pm_p1 if player_num == 1 else self.pm_p2
        net = self.net_p1 if player_num == 1 else self.net_p2
        w = self.p1_widgets if player_num == 1 else self.p2_widgets
        if pm.status != ProgramStatus.READY: return
        pm.start_running()
        w["lbl_prog_stat"].config(text=f"Selected: {pm.selected_program} | Status: RUNNING (STANDBY)")
        if net: net.send_program_update(pm.selected_program, ProgramStatus.RUNNING)

    def _on_state_update(self, data):
        self.lbl_timer.config(text=data.get("timer", "00:00"))
        f_state = data.get("field_state", "DISABLED")
        self.lbl_field_state.config(text=f"FIELD STATE: {f_state}")
        channels = data.get("channels", {})
        self._update_auth_box(self.p1_widgets, self.r1_id, channels.get(self.p1_id, {}))
        self._update_auth_box(self.p2_widgets, self.r2_id, channels.get(self.p2_id, {}))

    def _update_auth_box(self, widgets, robot_id, ch_data):
        r_state = ch_data.get("robot_state", "DISABLED")
        indiv = ch_data.get("individually_disabled", False)

        if indiv:
            widgets["lbl_perm"].config(text=f"{robot_id} INDIVIDUALLY DISABLED BY GAME MASTER 🛑", fg="#EF4444")
            widgets["auth_box"].config(bg="#3B0707")
        elif r_state == "DRIVER_CONTROL":
            widgets["lbl_perm"].config(text=f"{robot_id} CONTROL AUTHORIZED (DRIVER ENABLED) ✓", fg="#10B981")
            widgets["auth_box"].config(bg="#022C22")
        elif r_state == "AUTONOMOUS":
            widgets["lbl_perm"].config(text=f"{robot_id} AUTONOMOUS ROUTINE (INPUTS LOCKED) ⚡", fg="#D97706")
            widgets["auth_box"].config(bg="#2E1C03")
        elif r_state == "EMERGENCY_STOP":
            widgets["lbl_perm"].config(text=f"{robot_id} EMERGENCY STOPPED ⚠️", fg="#EF4444")
            widgets["auth_box"].config(bg="#3B0707")
        else:
            widgets["lbl_perm"].config(text=f"{robot_id} STANDBY (DISABLED BY REFEREE)", fg="#F59E0B")
            widgets["auth_box"].config(bg="#1E293B")