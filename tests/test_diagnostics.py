import unittest
from pathlib import Path

from diagnostics import Reading, deviation_counts, load_readings
from evidence import investigate, validate_sources


class DiagnosticsTests(unittest.TestCase):
    def test_limits_are_inclusive(self):
        for value in (1.0, 2.0):
            with self.subTest(value=value):
                self.assertEqual(Reading("R", "S", "U", "P", value, 1.0, 2.0).status, "IN_RANGE")
        for value in (0.9, 2.1):
            with self.subTest(value=value):
                self.assertEqual(Reading("R", "S", "U", "P", value, 1.0, 2.0).status, "OUT_OF_RANGE")

    def test_incomplete_or_invalid_data_is_unknown(self):
        for value, lower, upper in ((None, 1, 2), (1, None, 2), (1, 2, 1), (float("nan"), 1, 2)):
            with self.subTest(value=value, lower=lower, upper=upper):
                self.assertEqual(Reading("R", "S", "U", "P", value, lower, upper).status, "UNKNOWN")

    def test_isolated_case_keeps_cause_undetermined(self):
        counts = deviation_counts(self.isolated_case)
        result = investigate(self.isolated_case)
        self.assertEqual((len(self.isolated_case), len(counts)), (80, 8))
        self.assertEqual(sorted(counts.values()), [0] * 7 + [5])
        self.assertEqual((result.classification, result.confidence), ("UNDETERMINED", "LOW"))
        self.assertEqual(len(result.source_ids), 5)
        self.assertTrue(all(row.status == "OUT_OF_RANGE" for row in self.isolated_case if row.id in result.source_ids))

    def test_recurring_case_keeps_cause_undetermined(self):
        result = investigate([row for row in self.readings if row.station == "Demo B"])
        self.assertIn("recur across units", result.observation)
        self.assertEqual((result.classification, result.confidence), ("UNDETERMINED", "LOW"))

    def test_rejects_unknown_and_duplicate_references(self):
        registry = {row.id: row for row in self.isolated_case}
        source_id = self.isolated_case[0].id
        with self.assertRaisesRegex(ValueError, "Unknown"):
            validate_sources(("missing",), registry)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_sources((source_id, source_id), registry)

    @classmethod
    def setUpClass(cls):
        data = Path(__file__).resolve().parents[1] / "data" / "demo_measurements.csv"
        cls.readings = load_readings(data)
        cls.isolated_case = [row for row in cls.readings if row.station == "Demo A"]
