"""Deterministic tolerance checks for the bundled synthetic readings."""

import csv
from collections import Counter
from dataclasses import dataclass
from math import isfinite
from pathlib import Path


@dataclass(frozen=True)
class Reading:
    id: str
    station: str
    unit: str
    parameter: str
    value: float | None
    lower: float | None
    upper: float | None

    @property
    def status(self) -> str:
        value, lower, upper = self.value, self.lower, self.upper
        if any(number is None or not isfinite(number) for number in (value, lower, upper)):
            return "UNKNOWN"
        if lower > upper:
            return "UNKNOWN"
        if lower <= value <= upper:
            return "IN_RANGE"
        return "OUT_OF_RANGE"


def load_readings(path: Path) -> list[Reading]:
    with path.open(newline="", encoding="utf-8") as file:
        return [
            Reading(
                row["id"], row["station"], row["unit"], row["parameter"],
                *(float(row[key]) if row[key].strip() else None
                  for key in ("value", "lower", "upper")),
            )
            for row in csv.DictReader(file)
        ]


def deviation_counts(readings: list[Reading]) -> dict[str, int]:
    counts = Counter(row.unit for row in readings if row.status == "OUT_OF_RANGE")
    return {unit: counts[unit] for unit in sorted({row.unit for row in readings})}
