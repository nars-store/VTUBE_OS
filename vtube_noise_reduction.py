from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MixerTrack:
    name: str
    volume: float = 1.0
    muted: bool = False
    pan: float = 0.0
    enabled: bool = True
    source_type: str = "microphone"
    metadata: Dict[str, object] = field(default_factory=dict)

    def normalize(self) -> float:
        return 0.0 if self.muted or not self.enabled else max(0.0, min(1.5, self.volume))


class AudioMixer:
    """Simple mixer for mic, system audio, phone audio, and TTS tracks."""

    def __init__(self):
        self.tracks: Dict[str, MixerTrack] = {}

    def add_track(self, track: MixerTrack) -> None:
        self.tracks[track.name] = track

    def remove_track(self, name: str) -> None:
        self.tracks.pop(name, None)

    def set_volume(self, name: str, volume: float) -> None:
        if name in self.tracks:
            self.tracks[name].volume = max(0.0, min(2.0, volume))

    def set_muted(self, name: str, muted: bool) -> None:
        if name in self.tracks:
            self.tracks[name].muted = muted

    def mix_levels(self) -> Dict[str, float]:
        return {name: track.normalize() for name, track in self.tracks.items()}

    def master_level(self) -> float:
        levels = self.mix_levels().values()
        if not levels:
            return 0.0
        return sum(levels) / len(levels)


if __name__ == "__main__":
    mixer = AudioMixer()
    mixer.add_track(MixerTrack("mic", volume=0.9, source_type="microphone"))
    mixer.add_track(MixerTrack("game", volume=0.7, source_type="system"))
    mixer.add_track(MixerTrack("tts", volume=0.5, source_type="tts"))
    print(mixer.mix_levels())
    print(mixer.master_level())
