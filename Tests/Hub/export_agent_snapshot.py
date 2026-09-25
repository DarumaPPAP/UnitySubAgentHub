#!/usr/bin/env python3
"""Export active Hub manifests to UnityAgent's data-only SubAgent profile catalog."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import yaml

from validate_registry import ROOT, validate_repository


REGISTRY_PATH = Path("Registry/subagents.yaml")


def export_agent_catalog(root: Path = ROOT) -> dict[str, Any]:
    """Build the UnityAgent ReferenceImplementation profile snapshot from canonical manifests."""
    errors = validate_repository(root)
    if errors:
        raise ValueError("Hub registry is invalid:\n" + "\n".join(errors))

    registry = yaml.safe_load((root / REGISTRY_PATH).read_text(encoding="utf-8"))
    profiles: dict[str, dict[str, Any]] = {}
    snapshot_version = "1.0"
    for entry in registry["entries"]:
        manifest_path = root / Path(*entry["manifest"].split("/"))
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if manifest["lifecycle"] != "active":
            continue
        if manifest["schema_version"] == "2.0":
            snapshot_version = "2.0"

        identity = manifest["identity"]
        runtime = manifest["runtime_profile"]
        installation = manifest["installation"]
        activation = manifest["activation"]
        evidence = manifest["evidence"]
        primary_backend = next(backend for backend in manifest["backends"] if backend["primary"] is True)
        capabilities = [
            f"{capability['id']}.{operation}"
            for capability in manifest["capabilities"]
            for operation in capability["operations"]
        ]
        profiles[identity["id"]] = {
            "profile_id": identity["id"],
            "display_name": identity["name"],
            "provider_id": primary_backend["id"],
            "audience": runtime["audience"],
            "goal_type": runtime["goal_type"],
            "capabilities": capabilities,
            "primary_capability": runtime["primary_capability"],
            "required_evidence": list(evidence["runtime_types"]),
            "activation": {
                "install_mode": installation["mode"],
                "auto_install": installation["auto_install"],
                "required_environment": list(activation["required_before_resolution"]),
            },
            "evidence": dict(evidence["runtime_provenance"]),
        }
        if manifest["schema_version"] == "1.0":
            profiles[identity["id"]].update(scope=dict(runtime["scope"]),
                value=dict(runtime["value"]), approval=dict(runtime["approval"]))

    default_profile = registry["default_profile"]
    if default_profile not in profiles:
        raise ValueError(f"default profile is not active in the exported snapshot: {default_profile}")
    if snapshot_version == "2.0" and any("scope" in profile for profile in profiles.values()):
        raise ValueError("mixed v1/v2 active profiles require an explicit catalog migration")
    return {"schema_version": snapshot_version, "default_profile": default_profile, "profiles": profiles}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to export")
    parser.add_argument("--output", type=Path, help="write the snapshot to this path; stdout when omitted")
    args = parser.parse_args(argv)
    try:
        output = yaml.safe_dump(export_agent_catalog(args.repo_root.resolve()), sort_keys=False, allow_unicode=True, width=1000)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"UnityAgent profile snapshot written: {args.output}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
