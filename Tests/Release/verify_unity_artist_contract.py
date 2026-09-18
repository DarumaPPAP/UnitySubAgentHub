#!/usr/bin/env python3
"""Canonical static contract gate for ArtistSubAgent 0.0.1-beta."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
VERSION_PATH = ROOT / "VERSION"
PACKAGE_PATH = ROOT / "Packages/com.darumappap.unity-artist/package.json"
CLI_PROJECT = ROOT / "src/UnityArtist.Cli/UnityArtist.Cli.csproj"
CLI_SOURCE = ROOT / "src/UnityArtist.Cli/Program.cs"
EDITOR_ROOT = ROOT / "Packages/com.darumappap.unity-artist/Editor"
MATRIX_PATH = ROOT / "Tests/Compatibility/support-matrix.yaml"
GATE_EVIDENCE_PATH = ROOT / "Tests/Compatibility/cli-pipeline-gate-evidence.yaml"
MANIFEST_PATH = ROOT / "SubAgents/artist_subagent/manifest.yaml"
SURFACE_PATH = ROOT / "SubAgents/artist_subagent/contracts/backend-surface-contract.yaml"
REPO_SKILLS_ROOT = ROOT / ".agents/skills"
LEGACY_PLUGIN_ROOT = ROOT / ".agents/plugins/unity-artist"

REQUIRED_COMMANDS = {
    "help", "version", "doctor", "capabilities", "install", "inspect", "plan",
    "preview", "apply", "capture", "evaluate", "refine", "history", "cinematic",
}
FORBIDDEN_SOURCE_TOKENS = (
    "com.coplaydev.unity-mcp",
    "McpForUnityTool",
    "MCPForUnity",
    "using Unity.MCP",
    "AutoRegister",
)
EXPECTED_ROWS = {
    ("2022.3 LTS", "builtin"),
    ("Unity 6.x+", "builtin"),
    ("Unity 6.x+", "urp"),
    ("Unity 6.x+", "hdrp"),
}


def error(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"[ERROR] {message}")


def read_json(errors: list[str], path: Path) -> dict:
    if not path.is_file():
        error(errors, f"missing JSON file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        error(errors, f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        error(errors, f"JSON root must be an object: {path.relative_to(ROOT)}")
        return {}
    return value


def read_yaml(errors: list[str], path: Path) -> dict:
    if not path.is_file():
        error(errors, f"missing YAML file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        error(errors, f"invalid YAML {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        error(errors, f"YAML root must be a mapping: {path.relative_to(ROOT)}")
        return {}
    return value


def check_identity(errors: list[str]) -> None:
    version = VERSION_PATH.read_text(encoding="utf-8").strip() if VERSION_PATH.is_file() else ""
    package = read_json(errors, PACKAGE_PATH)
    if version != "0.0.1-beta":
        error(errors, f"VERSION must be 0.0.1-beta, got {version!r}")
    if package.get("name") != "com.darumappap.unity-artist":
        error(errors, "current package name is not com.darumappap.unity-artist")
    if package.get("version") != version:
        error(errors, "VERSION and UnityArtist package version disagree")
    dependencies = package.get("dependencies") or {}
    if "com.unity.pipeline" in dependencies:
        error(errors, "the core UnityArtist package must not force the Unity 6-only Pipeline dependency on Unity 2022.3")
    if dependencies:
        error(errors, f"current package dependencies must be empty so the bounded 2022.3 fallback can compile, got {sorted(dependencies)}")
    if package.get("unity") != "2022.3":
        error(errors, "package minimum Unity version must be 2022.3")


def check_cli_surface(errors: list[str]) -> None:
    source = CLI_SOURCE.read_text(encoding="utf-8") if CLI_SOURCE.is_file() else ""
    command_block = re.search(r"SupportedCommands.*?\{(?P<body>.*?)\};", source, re.DOTALL)
    commands = set(re.findall(r'"([a-z]+)"', command_block.group("body") if command_block else ""))
    missing = sorted(REQUIRED_COMMANDS - commands)
    if missing:
        error(errors, f"CLI is missing commands: {missing}")
    if '"official_unity_cli_pipeline"' not in source or '"official_unity_cli_bounded_batch_fallback"' not in source:
        error(errors, "CLI does not declare official_unity_cli_pipeline transport")
    if '"pipeline", "install"' not in source or '"command"' not in source:
        error(errors, "CLI does not expose install and official Pipeline command delegation")
    if not CLI_PROJECT.is_file():
        error(errors, "CLI project file is missing")


def check_editor_surface(errors: list[str]) -> None:
    sources = "\n".join(path.read_text(encoding="utf-8") for path in EDITOR_ROOT.rglob("*.cs")) if EDITOR_ROOT.is_dir() else ""
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in sources:
            error(errors, f"forbidden legacy/MCP token remains in current Editor source: {token}")
    if "CliCommand" not in sources or "Unity.Pipeline.Commands" not in sources:
        error(errors, "current Editor package does not expose official Pipeline CliCommand registrations")
    for command in ("artist.inspect", "artist.plan", "artist.preview", "artist.apply", "artist.capture", "artist.evaluate", "artist.refine", "artist.cinematic", "artist.history"):
        if command not in sources:
            error(errors, f"missing Pipeline command registration: {command}")
    for token in ("CinematicRequest", "InspectCinematicDirector", "CreateTrack", "CreateMarker", "SetGenericBinding", "Undo.RecordObject", "depth_channel", "object_id_channel", "UnityArtistBatchCommands", "bounded_non_mcp_batch_fallback"):
        if token not in sources:
            error(errors, f"current Editor source is missing bounded Artist/Cinematic contract token: {token}")
    compatibility = EDITOR_ROOT / "Compatibility/ArtistCompatibility.cs"
    compatibility_tests = ROOT / "Packages/com.darumappap.unity-artist/Tests/Editor/ArtistCompatibilityTests.cs"
    for path in (compatibility, compatibility_tests):
        if not path.is_file() or not Path(str(path) + ".meta").is_file():
            error(errors, f"compatibility asset or .meta is missing: {path.relative_to(ROOT)}")


def check_matrix(errors: list[str]) -> None:
    matrix = read_yaml(errors, MATRIX_PATH)
    rows = matrix.get("rows") or []
    actual = {(str(row.get("unity_version")), str(row.get("render_pipeline"))) for row in rows if isinstance(row, dict)}
    if actual != EXPECTED_ROWS:
        error(errors, f"formal release matrix drifted: {sorted(actual)}")
    if matrix.get("transport") != "official_unity_cli_pipeline":
        error(errors, "matrix transport must remain official_unity_cli_pipeline")
    if matrix.get("fallback_policy") != "concrete_cli_pipeline_gate_failure_only":
        error(errors, "fallback policy is not concrete CLI/Pipeline Gate Failure only")
    if matrix.get("verification_contract", {}).get("unsupported_result_before_mutation") is not True:
        error(errors, "unsupported result before mutation is not required")


def check_cli_pipeline_gate_evidence(errors: list[str]) -> None:
    evidence = read_yaml(errors, GATE_EVIDENCE_PATH)
    if evidence.get("case") != "unity-2022.3-builtin":
        error(errors, "CLI/Pipeline gate evidence must cover the 2022.3 Built-in case")
    candidate = evidence.get("official_first_candidate") or {}
    if candidate.get("transport") != "official_unity_cli_pipeline":
        error(errors, "2022.3 gate evidence must record Official Unity CLI + Pipeline as first candidate")
    pipeline = candidate.get("pipeline") or {}
    if pipeline.get("failure_class") != "concrete_cli_pipeline_gate_failure":
        error(errors, "2022.3 gate evidence must preserve a concrete Pipeline gate failure")
    plugin = evidence.get("artist_plugin") or {}
    if plugin.get("version_status") != "passed" or plugin.get("help_status") != "passed":
        error(errors, "Artist plugin version/help command evidence is incomplete")
    if plugin.get("global_help_status") != "blocked_by_official_cli_global_parser":
        error(errors, "global unity artist --help behavior must remain explicitly recorded")
    fallback = evidence.get("fallback_evaluation") or {}
    if fallback.get("selected") is not True or fallback.get("status") != "verified_bounded_non_mcp":
        error(errors, "2022.3 bounded fallback selection/evidence is incomplete")


def check_catalog(errors: list[str]) -> None:
    manifest = read_yaml(errors, MANIFEST_PATH)
    surface = read_yaml(errors, SURFACE_PATH)
    identity = manifest.get("identity") or {}
    if manifest.get("kind") != "subagent_manifest" or identity.get("name") != "ArtistSubAgent":
        error(errors, "canonical ArtistSubAgent manifest identity is invalid")
    if identity.get("id") != "artist_subagent" or identity.get("version") != "0.0.1-beta":
        error(errors, "canonical SubAgent id or release version is invalid")
    if manifest.get("lifecycle") != "active":
        error(errors, "ArtistSubAgent manifest must remain active")
    install = manifest.get("installation") or {}
    if install.get("mode") != "optional" or install.get("required") is not False or install.get("auto_install") is not False:
        error(errors, "ArtistSubAgent must remain optional and no-auto-install")
    activation = manifest.get("activation") or {}
    if activation.get("false_behavior") != "exclude_from_resolution" or activation.get("unknown_behavior") != "exclude_from_resolution":
        error(errors, "false or unknown ArtistSubAgent activation must be excluded from resolution")
    backends = manifest.get("backends") or []
    primary = [backend for backend in backends if backend.get("primary") is True]
    if len(primary) != 1 or primary[0].get("id") != "unity_artist_cli" or primary[0].get("id") == identity.get("id"):
        error(errors, "unity_artist_cli must remain a distinct primary backend id")
    if surface.get("kind") != "specialist_backend_surface_contract":
        error(errors, "Artist backend surface contract kind is invalid")
    if surface.get("backend_commands") and set(surface["backend_commands"]) != REQUIRED_COMMANDS:
        error(errors, "backend command set disagrees with CLI contract")
    forbidden = set(surface.get("forbidden_surface") or [])
    if not {"mcp_transport", "generic_gameobject_crud", "generic_hierarchy_crud", "arbitrary_eval"}.issubset(forbidden):
        error(errors, "backend surface must continue to forbid MCP and generic CRUD/eval")
    if surface.get("automatic_save") is not False or surface.get("arbitrary_eval") is not False:
        error(errors, "Artist backend surface must disable automatic save and arbitrary eval")

def check_agent_distribution(errors: list[str]) -> None:
    if LEGACY_PLUGIN_ROOT.exists():
        error(errors, "standalone .agents/plugins/unity-artist surface must be removed")
    expected = {
        "artist-subagent-cinematic-evidence",
        "artist-subagent-lookdev-refine",
        "artist-subagent-backend-setup",
    }
    actual = {
        path.parent.name
        for path in REPO_SKILLS_ROOT.rglob("SKILL.md")
        if path.parent.name.startswith("artist-subagent-")
    } if REPO_SKILLS_ROOT.is_dir() else set()
    missing = sorted(expected - actual)
    if missing:
        error(errors, f"repo-scoped ArtistSubAgent skills are missing: {missing}")
    production_roots = [
        ROOT / ".agents",
        ROOT / "Catalog",
        ROOT / "Specs",
        ROOT / "Packages",
        ROOT / "src",
    ]
    if any(
        path.name == ".mcp.json"
        for production_root in production_roots
        if production_root.exists()
        for path in production_root.rglob("*")
    ):
        error(errors, "ArtistSubAgent production surface must not contain .mcp.json")


def check_legacy_anchor(errors: list[str]) -> None:
    package = ROOT / "Legacy/MyUnityMCP-1.1.1/Package/package.json"
    value = read_json(errors, package)
    if value.get("version") != "1.1.1":
        error(errors, "Legacy MyUnityMCP v1.1.1 package anchor is missing or changed")
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/tags/v1.1.1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        error(errors, "immutable v1.1.1 tag is not present locally")


def main() -> int:
    errors: list[str] = []
    check_identity(errors)
    check_cli_surface(errors)
    check_editor_surface(errors)
    check_matrix(errors)
    check_cli_pipeline_gate_evidence(errors)
    check_catalog(errors)
    check_agent_distribution(errors)
    check_legacy_anchor(errors)
    print(f"ArtistSubAgent production contract: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
