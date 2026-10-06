"""
Manages robot code slot selection, ready states, and local program execution safety.
"""
from typing import List
from common.states import ProgramStatus

class ProgramManager:
    AVAILABLE_PROGRAMS: List[str] = [
        "Autonomous_1",
        "Autonomous_2",
        "Skills_Challenge",
        "Driver_Program"
    ]

    def __init__(self):
        self.selected_program: str = "None"
        self.status: ProgramStatus = ProgramStatus.NOT_SELECTED

    def select(self, name: str):
        if name in self.AVAILABLE_PROGRAMS:
            self.selected_program = name
            self.status = ProgramStatus.READY

    def start_running(self):
        if self.status == ProgramStatus.READY:
            # Crucial Rule: Running does NOT enable driver control!
            self.status = ProgramStatus.RUNNING