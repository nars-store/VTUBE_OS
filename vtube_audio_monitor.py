from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NoiseProfile:
    gate_threshold_db: float = -42.0
    suppression_db: float = 12.0
    compressor_ratio: float = 2.5
    limiter_db: float = -1.5
    hp_filter_hz: int = 80
    lp_filter_hz: int = 10000
    noise_gate_enabled: bool = True
    headphone_monitoring: bool = False


class NoiseReductionEngine:
    """A foundational engine for mic cleanup and live voice enhancement."""

    def __init__(self, profile: Optional[NoiseProfile] = None):
        self.profile = profile or NoiseProfile()

    def apply_gate(self, input_db: float) -> float:
        if not self.profile.noise_gate_enabled:
            return input_db
        if input_db < self.profile.gate_threshold_db:
            return -120.0
        return input_db

    def apply_suppression(self, input_db: float) -> float:
        if input_db <= self.profile.gate_threshold_db:
            return -120.0
        adjusted = input_db + self.profile.suppression_db
        return max(-120.0, min(0.0, adjusted))

    def apply_compression(self, input_db: float) -> float:
        if input_db <= -18.0:
            return input_db
        return input_db / self.profile.compressor_ratio

    def apply_limiter(self, input_db: float) -> float:
        return min(input_db, self.profile.limiter_db)

    def process(self, input_db: float) -> float:
        signal = self.apply_gate(input_db)
        signal = self.apply_suppression(signal)
        signal = self.apply_compression(signal)
        signal = self.apply_limiter(signal)
        return signal


if __name__ == "__main__":
    engine = NoiseReductionEngine()
    values = [-50.0, -18.0, -6.0, 0.0]
    print({value: engine.process(value) for value in values})
