# UnitySubAgentHub Repository Policy

## Authority and boundary

This repository owns the SubAgent registry, shared schemas, per-specialist manifests, lifecycle metadata, contract references, and validation. It is not a runtime, orchestrator, resolver, installer, or execution surface. UnityAgent is the only Control Plane and remains authoritative for policy, approval, environment discovery, binding, capability resolution, execution, retry/fallback, and evidence normalization.

`Registry/subagents.yaml` is the index. `SubAgents/<id>/manifest.yaml` is the source of truth for that specialist's identity, lifecycle, install mode, capabilities, compatibility, dependencies, backend references, and evidence requirements. Do not duplicate those facts in a second Hub catalog. Detailed specialist behavior may live in linked contracts.

## Required invariants

- Every specialist is optional. `required` must be false and `auto_install` must be false.
- Registry membership does not establish local installation, project binding, compatibility, or readiness.
- Uninstalled, incompatible, unbound, unavailable, false, or unknown activation checks exclude a specialist before ranking.
- No Hub or capability-resolution flow may automatically install or update a specialist. Setup is a separate, explicitly requested action.
- Only lifecycle `active` may be considered for new resolution. `deprecated`, `retired`, and `revoked` are excluded.
- `artist_subagent` and `unity_artist_cli` are different identities. Never route a SubAgent request by substituting its backend id.
- UnityAgent owns all runtime resolution and execution. Hub validators inspect metadata and referenced files only.
- Manifests and committed evidence use repository-relative paths. Never commit machine-specific paths or live installation state.
- Do not change `Legacy/MyUnityMCP-1.1.1/` or rewrite its published tag.

## Adding a specialist

Create one `SubAgents/<id>/manifest.yaml` that satisfies `Schemas/subagent-manifest.schema.json`, then add its path to `Registry/subagents.yaml`. Keep the manifest's backend ids separate from its specialist id. Use stable capability ids and declare all compatibility and evidence references. A new entry using the shared contract must not require UnityAgent source changes.

Do not add runtime dispatch, candidate ranking, local environment discovery, package installation, or project mutation to this repository's Hub validation path. New manifest paths must be covered by the shared validator and CI.

## Validation

Run:

```sh
python Tests/Hub/validate_registry.py
python -m unittest discover -s Tests/Hub -p 'test_*.py' -v
python Tests/Hub/export_agent_snapshot.py --output /tmp/subagent-catalog.yaml
```

The Hub workflow publishes a data-only profile snapshot for UnityAgent. The current UnityAgent profile resolver requires a unique profile for each capability, so overlapping active runtime capabilities are rejected until its contract supports ranking. This snapshot does not observe runtime installation, compatibility, binding, or readiness; UnityAgent must apply those checks against its own environment facts.

Keep the existing Artist gates green when changing its linked contracts:

```sh
python Tests/Release/verify_unity_artist_contract.py
python Tests/Compatibility/verify-unity-api-compatibility.py
python Tests/Release/verify_portable_paths.py
```

Compatibility-sensitive Artist code and API changes must apply `skills/unity-artist-unity-api-compatibility/SKILL.md`.

Direct Unity Editor, License, Pipeline, and visual end-to-end evidence must be distinguished from static host validation. Unknown observations must not be recorded as successful evidence.

## Artist backend compatibility

The first specialist's implementation remains in `Packages/com.darumappap.unity-artist/` and `src/UnityArtist.Cli/` during this Hub transition. Its backend contract and detailed workflow specification remain linked from `SubAgents/artist_subagent/manifest.yaml`.

Preserve its bounded typed-argument CLI, explicit project targeting, allowlisted commands, Unity Undo, no automatic save, no arbitrary evaluation, and concrete-gate-only fallback behavior. Compatibility-sensitive changes must keep the Editor implementation and EditMode tests together. These Artist-specific rules do not define additional Hub runtime behavior.
