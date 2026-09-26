from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Legacy/MyUnityMCP-1.1.1/Package/Editor"
MATRIX = ROOT / "Design/legacy-capability-salvage.csv"
TOOL = re.compile(r'\[McpForUnityTool\(\s*"([^"]+)"')
EXPECTED = {"graphics": 32, "agent": 10, "world": 3, "profiler": 8, "addressables": 4, "ui": 5, "animation": 5, "audio": 5, "cinematic": 5}


class LegacySalvageTests(unittest.TestCase):
    def test_source_inventory_matches_every_matrix_row(self) -> None:
        source_tools = [match.group(1) for path in SOURCE.rglob("*.cs") for match in TOOL.finditer(path.read_text(encoding="utf-8-sig"))]
        with MATRIX.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))

        self.assertEqual(len(source_tools), 77)
        self.assertEqual(Counter(name.split(".")[0] for name in source_tools), EXPECTED)
        self.assertEqual(len(rows), 77)
        self.assertEqual(Counter(row["legacy_tool"] for row in rows), Counter(source_tools))
        self.assertTrue(all(row["decision"] in {"REPLACED", "PORT", "KNOWLEDGE", "RETIRE"} for row in rows))
        for row in rows:
            with self.subTest(tool=row["legacy_tool"]):
                self.assertTrue(all(row[field] for field in ("legacy_module", "responsibility", "current_equivalent", "current_owner", "gap", "target_owner", "migration_risk", "replacement_evidence", "source")))
                self.assertTrue((ROOT / row["source"]).is_file())


if __name__ == "__main__":
    unittest.main()
