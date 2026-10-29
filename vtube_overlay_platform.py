from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DonationEvent:
    donor_name: str
    amount: float
    currency: str = "IDR"
    message: str = ""
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "donor_name": self.donor_name,
            "amount": self.amount,
            "currency": self.currency,
            "message": self.message,
            "source": self.source,
            "metadata": self.metadata,
        }


class DonationConnector:
    """Foundational donation event intake for VTUBE OS platform support."""

    def __init__(self):
        self.events: List[DonationEvent] = []
        self.targets: Dict[str, float] = {}

    def add_target(self, name: str, amount: float) -> None:
        self.targets[name] = amount

    def add_event(self, event: DonationEvent) -> DonationEvent:
        self.events.append(event)
        return event

    def total_donations(self) -> float:
        return sum(event.amount for event in self.events)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "total": self.total_donations(),
            "targets": self.targets,
            "events": [event.as_dict() for event in self.events],
        }


if __name__ == "__main__":
    connector = DonationConnector()
    connector.add_target("bday-goal", 2500000)
    connector.add_event(DonationEvent("Rizky", 50000, "IDR", "Semangat live!", "kofi"))
    print(connector.snapshot())
