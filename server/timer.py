"""
High-resolution authoritative timer with drift compensation and callback triggers.
"""
import asyncio
import time
from typing import Callable, Optional

class MatchTimer:
    def __init__(self, on_tick: Optional[Callable[[str, int], None]] = None, on_expire: Optional[Callable[[], None]] = None):
        self.on_tick = on_tick
        self.on_expire = on_expire
        self.remaining_seconds: int = 0
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None

    @property
    def display_str(self) -> str:
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def set_duration(self, seconds: int):
        self.remaining_seconds = seconds

    def start(self, seconds: Optional[int] = None):
        if seconds is not None:
            self.remaining_seconds = seconds
        self.is_running = True
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(self._run_loop())

    def pause(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

    def reset(self, seconds: int = 0):
        self.pause()
        self.remaining_seconds = seconds

    async def _run_loop(self):
        try:
            while self.is_running and self.remaining_seconds > 0:
                if self.on_tick:
                    self.on_tick(self.display_str, self.remaining_seconds)
                await asyncio.sleep(1.0)
                self.remaining_seconds -= 1

            if self.is_running and self.remaining_seconds <= 0:
                self.is_running = False
                if self.on_tick:
                    self.on_tick(self.display_str, 0)
                if self.on_expire:
                    self.on_expire()
        except asyncio.CancelledError:
            pass