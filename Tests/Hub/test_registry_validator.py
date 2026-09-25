from __future__ import annotations

import shutil
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from validate_registry import validate_repository


def manifest(subagent_id: str, backend_id: str) -> dict:
    capability_prefix = subagent_id.removesuffix("_subagent")
    return {
        "schema_version": "3.0",
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
        "backends": [{"id": backend_id, "kind": "cli", "executable": backend_id, "contract_ref": "Contracts/backend.yaml"}],
        "evidence": {
            "required": True,
            "required_artifacts": ["provider_result"],
            "runtime_types": ["state_observation"],
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
        for name in ("subagent-manifest.schema.json", "subagent-registry.schema.json", "subagent-catalog-snapshot.schema.json"):
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
        key = "kind: subagent_registry\n"
        self.assertIn(key, text)
        path.write_text(text.replace(key, "kind: other\n" + key, 1), encoding="utf-8")

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

    def test_hub_governance_changes_trigger_contract_validation(self) -> None:
        root = Path(__file__).resolve().parents[2]
        workflow = yaml.load(
            (root / ".github/workflows/subagent-hub-contract.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )

        for event in ("pull_request", "push"):
            paths = workflow["on"][event]["paths"]
            self.assertIn("AGENTS.md", paths)
            self.assertIn("README.md", paths)
            self.assertIn("Design/**", paths)
            self.assertIn("Schemas/**", paths)

    def test_release_gate_covers_canonical_manifest_changes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        workflow = (root / ".github/workflows/release-gate.yml").read_text(encoding="utf-8")

        self.assertIn("      - SubAgents/**", workflow)

    def test_artist_manifest_does_not_define_consumer_runtime_profile(self) -> None:
        root = Path(__file__).resolve().parents[2]
        manifest = yaml.safe_load((root / "SubAgents/artist_subagent/manifest.yaml").read_text(encoding="utf-8"))

        self.assertNotIn("runtime_profile", manifest)
        self.assertNotIn("runtime_provenance", manifest["evidence"])
        self.assertNotIn("primary", manifest["backends"][0])

    def test_current_artist_support_is_unity6_pipeline_only(self) -> None:
        root = Path(__file__).resolve().parents[2]
        manifest = yaml.safe_load((root / "SubAgents/artist_subagent/manifest.yaml").read_text(encoding="utf-8"))
        matrix = yaml.safe_load((root / "Tests/Compatibility/support-matrix.yaml").read_text(encoding="utf-8"))
        package = json.loads((root / "Packages/com.darumappap.unity-artist/package.json").read_text(encoding="utf-8"))
        targets = {(item["unity_version"], item["render_pipeline"]) for item in manifest["compatibility"]["supported_targets"]}
        rows = {(item["unity_version"], item["render_pipeline"]) for item in matrix["rows"]}
        expected = {("Unity 6.x+", pipeline) for pipeline in ("builtin", "urp", "hdrp")}
        self.assertEqual(targets, expected)
        self.assertEqual(rows, expected)
        self.assertEqual(package["unity"], "6000.0")
        backend = manifest["backends"][0]
        self.assertEqual(backend["transport"], "official_unity_cli_pipeline")
        self.assertNotIn("fallback_transport", backend)
        self.assertIn("unity_artist_cli.pipeline_reachable", manifest["activation"]["required_before_resolution"])
        self.assertTrue(any(item["id"] == "com.unity.pipeline" for item in manifest["dependencies"]))

    def test_hub_snapshot_contains_static_artist_contract_only(self) -> None:
        from export_agent_snapshot import export_hub_snapshot, validate_snapshot
        root = Path(__file__).resolve().parents[2]
        manifest = yaml.safe_load((root / "SubAgents/artist_subagent/manifest.yaml").read_text(encoding="utf-8"))
        snapshot = export_hub_snapshot(root)
        artist = snapshot["specialists"][0]["manifest"]
        self.assertEqual(manifest["schema_version"], "3.0")
        self.assertEqual(snapshot["kind"], "subagent_catalog_snapshot")
        self.assertEqual(artist, manifest)
        self.assertEqual([], validate_snapshot(snapshot, root))
        for name in ("runtime_profile", "goal_type", "primary_capability", "audience"):
            self.assertNotIn(name, artist)
        self.assertNotIn("default_profile", snapshot)
        self.assertFalse((root / "SubAgents/artist_subagent/contracts/camera-fov-reference-profile.yaml").exists())

    def test_hub_setup_guidance_uses_unityagent_approval_gate(self) -> None:
        root = Path(__file__).resolve().parents[2]
        skill = (root / ".agents/skills/artist-subagent-backend-setup/SKILL.md").read_text(encoding="utf-8")
        guide = (root / "SubAgents/artist_subagent/README.md").read_text(encoding="utf-8")
        self.assertIn("unity-agent setup --operation plan", skill)
        self.assertIn("unity-agent setup --operation apply", skill)
        self.assertNotIn("unity artist install --project-path", skill)
        self.assertIn("Runtime/ReferenceImplementation/subagent-catalog.yaml", guide)
        self.assertNotIn("`unity_artist_cli` Profile", guide)

    def write_registry(self) -> None:
        entries = "\n".join(f"  - manifest: {path}" for path in self.manifests)
        (self.root / "Registry/subagents.yaml").write_text(
            "schema_version: '2.0'\n"
            "kind: subagent_registry\n"
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
        registry["runtime"] = {"owns_execution": True}
        registry_path.write_text(__import__("yaml").safe_dump(registry, sort_keys=False), encoding="utf-8")

        errors = validate_repository(self.root)

        self.assertTrue(any("unexpected property 'runtime'" in error for error in errors))

    def test_registry_rejects_consumer_profile_selection(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.write_registry()
        registry_path = self.root / "Registry/subagents.yaml"
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        registry["default_profile"] = "artist_subagent"
        registry_path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

        errors = validate_repository(self.root)

        self.assertTrue(any("unexpected property 'default_profile'" in error for error in errors))

    def test_snapshot_includes_active_and_deprecated_contracts(self) -> None:
        from export_agent_snapshot import export_hub_snapshot

        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        shader_path = self.root / "SubAgents/shader_subagent/manifest.yaml"
        shader = __import__("yaml").safe_load(shader_path.read_text(encoding="utf-8"))
        shader["lifecycle"] = "deprecated"
        shader_path.write_text(__import__("yaml").safe_dump(shader, sort_keys=False), encoding="utf-8")
        self.write_registry()

        snapshot = export_hub_snapshot(self.root)

        self.assertEqual(["artist_subagent", "shader_subagent"], [item["manifest"]["identity"]["id"] for item in snapshot["specialists"]])
        self.assertEqual("deprecated", snapshot["specialists"][1]["manifest"]["lifecycle"])
        self.assertNotIn("default_profile", snapshot)

    def test_overlapping_capabilities_are_valid_hub_metadata(self) -> None:
        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.add_manifest("shader_subagent", "unity_shader_cli")
        shader_path = self.root / "SubAgents/shader_subagent/manifest.yaml"
        shader = __import__("yaml").safe_load(shader_path.read_text(encoding="utf-8"))
        shader["capabilities"][0]["id"] = "artist"
        shader_path.write_text(__import__("yaml").safe_dump(shader, sort_keys=False), encoding="utf-8")
        self.write_registry()

        self.assertEqual([], validate_repository(self.root))

    def test_snapshot_rejects_consumer_runtime_fields(self) -> None:
        from export_agent_snapshot import export_hub_snapshot, validate_snapshot

        self.add_manifest("artist_subagent", "unity_artist_cli")
        self.write_registry()
        snapshot = export_hub_snapshot(self.root)
        snapshot["specialists"][0]["manifest"]["runtime_profile"] = {"goal_type": "artist.inspect"}

        self.assertTrue(any("unexpected property 'runtime_profile'" in error for error in validate_snapshot(snapshot, self.root)))


if __name__ == "__main__":
    unittest.main()
