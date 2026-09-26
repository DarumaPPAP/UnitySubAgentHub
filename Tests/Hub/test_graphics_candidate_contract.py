from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class GraphicsCandidateContractTests(unittest.TestCase):
    def test_candidate_is_read_only_and_not_registered(self) -> None:
        contract = yaml.safe_load((ROOT / "SubAgents/graphics_subagent/contracts/capability-contracts.yaml").read_text(encoding="utf-8"))
        registry = yaml.safe_load((ROOT / "Registry/subagents.yaml").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "pilot_unregistered")
        self.assertEqual(set(contract["capabilities"]), {"graphics.inspect", "graphics.diagnose", "graphics.validate"})
        self.assertTrue(all(capability["mode"] == "read_only" for capability in contract["capabilities"].values()))
        self.assertEqual(contract["boundaries"]["mutation"], "prohibited_during_pilot")
        self.assertEqual(contract["evidence"]["unobserved_runtime"], "NOT_EVALUATED_RUNTIME")
        self.assertFalse(any("graphics_subagent" in entry["manifest"] for entry in registry["entries"]))


if __name__ == "__main__":
    unittest.main()
