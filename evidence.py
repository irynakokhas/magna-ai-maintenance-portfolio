"""Validate citations and summarise the pattern they support."""

from collections import Counter
from dataclasses import dataclass

from diagnostics import Reading


@dataclass(frozen=True)
class Finding:
    observation: str
    next_check: str
    source_ids: tuple[str, ...]
    classification: str = "UNDETERMINED"
    confidence: str = "LOW"


def validate_sources(source_ids: tuple[str, ...], registry: dict[str, Reading]) -> None:
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("Duplicate evidence references.")
    invalid_ids = set(source_ids) - registry.keys()
    if invalid_ids:
        raise ValueError(f"Unknown evidence references: {', '.join(sorted(invalid_ids))}")


def investigate(readings: list[Reading]) -> Finding:
    registry = {row.id: row for row in readings}
    if len(registry) != len(readings):
        raise ValueError("Reading IDs must be unique.")

    deviations = [row for row in readings if row.status == "OUT_OF_RANGE"]
    affected_units = {row.unit for row in deviations}
    observed = deviations or readings
    sources = tuple(row.id for row in observed)
    validate_sources(sources, registry)

    if not affected_units:
        return Finding(
            "No deviations were found in readings with usable limits.",
            "Review any unknown readings and check whether the available records cover the reported event.",
            sources,
        )
    if len(affected_units) == 1:
        return Finding(
            f"All {len(deviations)} recorded deviations occur on one unit.",
            "Compare adjacent units and reconcile the unit history with technician observations.",
            sources,
        )

    parameter_units = {
        (row.parameter, row.unit) for row in deviations
    }
    frequencies = Counter(parameter for parameter, _ in parameter_units)
    recurring = sorted(parameter for parameter, count in frequencies.items() if count > 1)
    if recurring:
        return Finding(
            f"Deviations recur across units for {', '.join(recurring)}.",
            "Review shared process conditions and corroborate the pattern with inspection records.",
            sources,
        )
    return Finding(
        "Several units show deviations, with no parameter recurring across units.",
        "Collect additional records to check for a recurring parameter or shared process condition.",
        sources,
    )

