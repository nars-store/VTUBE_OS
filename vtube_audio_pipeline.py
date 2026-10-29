from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AudioLevel:
    peak_db: float = -60.0
    rms_db: float = -60.0
    clipping: bool = False
    active: bool = False

    def as_dict(self) -> Dict[str, float | bool]:
        return {
            "peak_db": self.peak_db,
            "rms_db": self.rms_db,
            "clipping": self.clipping,
            "active": self.active,
        }


class AudioMonitor:
    """Monitor microphone, system audio, and phone microphone signal levels."""

    def __init__(self):
        self.levels: Dict[str, AudioLevel] = {}

    def update(self, name: str, peak_db: float, rms_db: float, clipping: bool = False) -> AudioLevel:
        level = AudioLevel(
            peak_db=peak_db,
            rms_db=rms_db,
            clipping=clipping,
            active=(peak_db > -50.0 or rms_db > -50.0),
        )
        self.levels[name] = level
        return level

    def snapshot(self) -> Dict[str, Dict[str, float | bool]]:
        return {name: level.as_dict() for name, level in self.levels.items()}


if __name__ == "__main__":
    monitor = AudioMonitor()
    print(monitor.update("mic", -18.0, -22.0, False).as_dict())
    print(monitor.snapshot())
