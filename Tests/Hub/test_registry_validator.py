from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from validate_registry import validate_repository


def manifest(subagent_id: str, backend_id: str) -> dict:
    capability_prefix = subagent_id.removesuffix("_subagent")
    primary_capability = f"{capability_prefix}.inspect"
    return {
        "schema_version": "1.0",
        "kind": "subagent_manifest",
        "identity": {"id": subagent_id, "name": subagent_id.replace("_", " ").title(), "version": "1.0.0"},
        "lifecycle": "active",
        "installation": {"mode": "optional", "required": False, "auto_install": False},
        "activation": {
            "required_before_resolution": ["backend_available", "project_bound"],
            "false_behavior": "exclude_from_resolution",
            "unknown_behavior": "exclude_from_resolution",
        },
        "capabilities": [{"id": capability_prefix, "operations": ["inspect"]}],
        "capability_contract_ref": "Contracts/capabilities.yaml",
        "compatibility": {
            "supported_targets": [{"unity_version": "Unity 6.x+", "render_pipeline": "builtin"}],
            "support_matrix_ref": "Contracts/support-matrix.yaml",
        },
        "dependencies": [
            {"id": backend_id, "kind": "backend", "required": True, "eligibility_gate": "backend_available"}
        ],
        "backends": [{"id": backend_id, "kind": "cli", "primary": True, "executable": backend_id, "contract_ref": "Contracts/backend.yaml"}],
        "runtime_profile": {
            "audience": subagent_id,
            "goal_type": primary_capability,
            "primary_capability": primary_capability,
            "scope": {
                "default_target_guid": "asset-guid-001",
                "component_type": "Example.Component",
                "property_paths": ["Example.value"],
                "mutation_channels": ["typed_property"],
                "max_targets": 1,
            },
            "value": {"type": "float", "unit": "normalized", "minimum": 0, "maximum": 1, "maximum_exclusive": True},
            "approval": {"default_minimum": 0, "default_maximum": 1, "minimum_exclusive": False, "maximum_exclusive": True},
        },
        "evidence": {
            "required": True,
            "required_artifacts": ["provider_result"],
            "runtime_types": ["state_observation"],
            "runtime_provenance": {"source_type": "example", "producer": "UnityAgent.Example.v1", "provenance_token": subagent_id},
            "terminal_states": ["verified", "partial_verified", "blocked_by_environment"],
            "contract_ref": "Contracts/evidence.yaml",
        },
    }


class RegistryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "Schemas").mkdir()
        (self.root / "Registry").mkdir()
        (self.root / "Contracts").mkdir()
        schema_root = Path(__file__).resolve().parents[2] / "Schemas"
        for name in ("subagent-manifest.schema.json", "subagent-registry.schema.json"):
            shutil.copyfile(schema_root / name, self.root / "Schemas" / name)
        for contract in ("support-matrix.yaml", "backend.yaml", "evidence.yaml", "capabilities.yaml"):
            (self.root / "Contracts" / contract).write_text("kind: test\n", encoding="utf-8")
        self.manifests: list[str] = []

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_duplicate_yaml_keys_are_rejected_in_registry(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.write_registry()
        path = self.root / "Registry/subagents.yaml"
        text = path.read_text(encoding="utf-8")
        key = "  unknown_behavior: exclude_from_resolution\n"
        self.assertIn(key, text)
        path.write_text(text.replace(key, "  unknown_behavior: allow\n" + key, 1), encoding="utf-8")

        errors = validate_repository(self.root)

        self.assertTrue(any("duplicate YAML key" in error for error in errors))

    def test_duplicate_yaml_keys_are_rejected_in_manifest(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.write_registry()
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        text = path.read_text(encoding="utf-8")
        key = "  unknown_behavior: exclude_from_resolution\n"
        self.assertIn(key, text)
        path.write_text(text.replace(key, "  unknown_behavior: allow\n" + key, 1), encoding="utf-8")

        errors = validate_repository(self.root)

        self.assertTrue(any("duplicate YAML key" in error for error in errors))

    def test_release_gate_covers_canonical_manifest_changes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        workflow = (root / ".github/workflows/release-gate.yml").read_text(encoding="utf-8")

        self.assertRegex(workflow, r"(?m)^\\s*- SubAgents/\\*\\*\\s*$")

    def test_checked_in_artist_producer_matches_current_unityagent_reference_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        manifest = yaml.safe_load((root / "SubAgents/artist_subagent/manifest.yaml").read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["evidence"]["runtime_provenance"]["producer"],
            "UnityAgent.ReferenceImplementation.v1.1",
        )

    def write_registry(self) -> None:
        entries = "\n".join(f"  - manifest: {path}" for path in self.manifests)
        (self.root / "Registry/subagents.yaml").write_text(
            "schema_version: '1.0'\n"
            "kind: subagent_registry\n"
            "control_plane: unity_agent\n"
            "runtime: {owns_execution: false, owns_resolution: false, auto_install: false}\n"
            "resolution:\n"
            "  phase_order: [registered, discovered, installed, compatible, project_bound, available, eligible, ranked]\n"
            "  eligible_lifecycle: active\n"
            "  unknown_behavior: exclude_from_resolution\n"
            "  unavailable_behavior: exclude_from_resolution\n"
            "  auto_install: false\n"
            "default_profile: artist_subagent\n"
            f"entries:\n{entries}\n",
            encoding="utf-8",
        )

    def add_manifest(self, subagent_id: str, backend_id: str) -> None:
        path = f"SubAgents/{subagent_id}/manifest.yaml"
        manifest_path = self.root / path
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(__import__("yaml").safe_dump(manifest(subagent_id, backend_id), sort_keys=False), encoding="utf-8")
        self.manifests.append(path)

    def test_registry_accepts_multiple_independent_optional_subagents(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        self.write_registry()

        self.assertEqual([], validate_repository(self.root))

    def test_unindexed_manifest_is_rejected(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        self.manifests.pop()
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("registry entries do not cover all manifests" in error for error in errors))

    def test_auto_install_is_rejected(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["installation"]["auto_install"] = True
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("must not auto-install" in error for error in errors))

    def test_required_installation_is_rejected(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["installation"]["required"] = True
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("specialist installation must remain optional" in error for error in errors))

    def test_required_dependency_must_declare_a_pre_resolution_gate(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["dependencies"][0].pop("eligibility_gate")
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("eligibility_gate is required for required dependencies" in error for error in errors))

    def test_required_backend_dependency_must_reference_a_declared_backend(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["dependencies"][0]["id"] = "missing_backend"
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("backend dependency" in error and "missing_backend" in error for error in errors))

    def test_primary_backend_must_have_a_required_dependency_gate(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["dependencies"] = []
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("primary backend" in error and "required dependency" in error for error in errors))

    def test_malformed_required_dependency_gate_is_reported_without_crashing(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["dependencies"][0]["eligibility_gate"] = ["backend_available"]
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("dependencies[0].eligibility_gate" in error for error in errors))

    def test_malformed_activation_gate_is_reported_without_crashing(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["activation"]["required_before_resolution"] = [["backend_available"]]
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("activation.required_before_resolution" in error for error in errors))

    def test_backend_id_must_be_distinct_from_subagent_id(self) -> None:
        self.add_manifest("artist_subagent", "artist_subagent")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("backend identity must differ" in error for error in errors))

    def test_unknown_activation_must_fail_closed(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        path = self.root / "SubAgents/artist_subagent/manifest.yaml"
        value = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
        value["activation"]["unknown_behavior"] = "allow"
        path.write_text(__import__("yaml").safe_dump(value, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("unknown activation checks must exclude" in error for error in errors))

    def test_hub_must_not_own_execution(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.write_registry()
        registry_path = self.root / "Registry/subagents.yaml"
        registry = __import__("yaml").safe_load(registry_path.read_text(encoding="utf-8"))
        registry["runtime"]["owns_execution"] = True
        registry_path.write_text(__import__("yaml").safe_dump(registry, sort_keys=False), encoding="utf-8")

        errors = validate_repository(self.root)

        self.assertTrue(any("Hub must not own SubAgent execution" in error for error in errors))

    def test_runtime_snapshot_includes_multiple_active_profiles_and_excludes_inactive(self) -> None:
        from export_agent_snapshot import export_agent_catalog

        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        shader_path = self.root / "SubAgents/shader_subagent/manifest.yaml"
        shader = __import__("yaml").safe_load(shader_path.read_text(encoding="utf-8"))
        shader["lifecycle"] = "deprecated"
        shader_path.write_text(__import__("yaml").safe_dump(shader, sort_keys=False), encoding="utf-8")
        self.write_registry()

        catalog = export_agent_catalog(self.root)

        self.assertEqual("artist_subagent", catalog["default_profile"])
        self.assertEqual({"artist_subagent"}, set(catalog["profiles"]))
        artist = catalog["profiles"]["artist_subagent"]
        self.assertEqual(
            {
                "profile_id", "display_name", "provider_id", "audience", "goal_type", "capabilities",
                "primary_capability", "required_evidence", "activation", "scope", "value", "approval", "evidence",
            },
            set(artist),
        )
        self.assertEqual("unity_artist_cli", artist["provider_id"])
        self.assertFalse(artist["activation"]["auto_install"])
        self.assertEqual(["artist.inspect"], artist["capabilities"])

    def test_duplicate_runtime_capabilities_are_rejected_until_agent_can_rank_profiles(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        shader_path = self.root / "SubAgents/shader_subagent/manifest.yaml"
        shader = __import__("yaml").safe_load(shader_path.read_text(encoding="utf-8"))
        shader["capabilities"][0]["id"] = "artist"
        shader["runtime_profile"]["goal_type"] = "artist.inspect"
        shader["runtime_profile"]["primary_capability"] = "artist.inspect"
        shader_path.write_text(__import__("yaml").safe_dump(shader, sort_keys=False), encoding="utf-8")
        self.write_registry()

        errors = validate_repository(self.root)

        self.assertTrue(any("active SubAgent runtime capabilities must be unique" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
