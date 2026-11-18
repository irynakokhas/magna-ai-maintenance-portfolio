"""Interactive portfolio demo using synthetic station data."""

from dataclasses import asdict
from pathlib import Path

import streamlit as st

from diagnostics import deviation_counts, load_readings
from evidence import investigate


st.set_page_config(page_title="MAGNA maintenance diagnostics", layout="wide")
st.title("Maintenance diagnostics")
st.caption("MAGNA portfolio demo • Synthetic measurements")
st.write("Compare readings against tolerance limits and inspect the evidence behind a preliminary finding.")

readings = load_readings(Path(__file__).parent / "data" / "demo_measurements.csv")
station = st.selectbox("Demo station", sorted({row.station for row in readings}))
selected = [row for row in readings if row.station == station]
counts = deviation_counts(selected)
finding = investigate(selected)

total, deviations, affected, unknown = st.columns(4)
total.metric("Readings", len(selected))
deviations.metric("Out of range", sum(counts.values()))
affected.metric("Affected units", f"{sum(count > 0 for count in counts.values())} / {len(counts)}")
unknown.metric("Unknown", sum(row.status == "UNKNOWN" for row in selected))

st.subheader("Deviations by unit")
st.bar_chart(
    [{"Unit": unit, "Deviations": count} for unit, count in counts.items()],
    x="Unit",
    y="Deviations",
    alt="Number of out-of-range readings for each unit at the selected station.",
)

st.subheader("Preliminary finding")
st.info(f"Cause {finding.classification.lower()} · {finding.confidence.lower()} confidence")
st.write(finding.observation)
st.markdown(f"**Suggested next check**  \n{finding.next_check}")

st.subheader("Measurement evidence")
cited_only = st.checkbox("Show only readings cited in the finding", value=True)
source_ids = set(finding.source_ids)
table = [
    {k: v for k, v in asdict(row).items() if k != "station"} | {"status": row.status}
    for row in selected
    if not cited_only or row.id in source_ids
]
st.dataframe(table, hide_index=True, alt="Measurement IDs, unit IDs, values, tolerances and diagnostic statuses.")
