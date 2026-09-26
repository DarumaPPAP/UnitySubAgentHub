from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class PerformanceCandidateContractTests(unittest.TestCase):
    def test_candidate_is_read_only_and_unregistered(self) -> None:
        contract = yaml.safe_load((ROOT / "SubAgents/performance_subagent/contracts/capability-contracts.yaml").read_text(encoding="utf-8"))
        registry = yaml.safe_load((ROOT / "Registry/subagents.yaml").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "pilot_unregistered")
        self.assertEqual(contract["identity"], "performance_subagent")
        self.assertEqual(set(contract["capabilities"]), {"performance.analyze"})
        self.assertEqual(contract["capabilities"]["performance.analyze"]["mode"], "read_only")
        self.assertEqual(contract["evidence"]["required_type"], "performance_analysis")
        self.assertEqual(contract["evidence"]["unobserved_runtime"], "NOT_EVALUATED_RUNTIME")
        self.assertEqual(contract["boundaries"]["provider_resolution"], "unity_agent_tool_broker_only")
        self.assertEqual(contract["boundaries"]["mutation"], "prohibited_during_pilot")
        self.assertFalse(any("performance_subagent" in entry["manifest"] for entry in registry["entries"]))


if __name__ == "__main__":
    unittest.main()
