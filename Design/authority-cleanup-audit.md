# Authority cleanup audit (2026-09-26)

## Classification

| Surface | Decision | Evidence and ownership |
|---|---|---|
| `Registry/`, `Schemas/`, `SubAgents/*/manifest.yaml`, `Tests/Hub/` | KEEP | Static specialist identity, contracts and validation belong to the Hub. |
| `Tests/Routing/cases.yaml` | DELETE from Hub; MOVE routing coverage to UnityAgent | The file declared `expected_primary_route`; UnityAgent owns routes in `Orchestration/Routing/task-routes.yaml`. No Hub code referenced the fixture. |
| `SubAgents/artist_subagent/contracts/camera-fov-reference-profile.yaml` | DELETE | A fixed camera GUID, property and approval range were historical task fixtures. Only a Hub test asserted that the file existed. |
| `Templates/AcceptanceProfiles/balanced-graphics.json` | DELETE | No active repository or UnityAgent reference was found. Scores and budgets are project evaluation policy, not registry metadata. |
| Eight forwarding scripts in `Tests/Release/` | DELETE | Each only imported `verify_unity_artist_contract.main`; no active workflow or non-Legacy source referenced their filenames. The canonical validator remains. |
| Artist package, CLI, compatibility tests, release scripts, install scripts and Artist workflows | MIGRATION CANDIDATE; retain co-located | Artist backend product owns these surfaces. UnityAgent's `release_installer.py` downloads `v0.0.1-beta` from this repository, and the Hub release workflow publishes the corresponding archive. Moving them now would change a live distribution URL. |
| `Legacy/MyUnityMCP-1.1.1/` | MIGRATION CANDIDATE; retain for now | `Tests/Release/verify_unity_artist_contract.py` reads `Legacy/MyUnityMCP-1.1.1/Package/package.json` as an active release gate. Remove that dependency before detaching the tree. |

## Contract decisions

- **FACT (before vNext):** The previous Hub exporter emitted `SubAgentProfileCatalog` fields including `default_profile`, `audience`, `goal_type`, `primary_capability` and a primary Provider. UnityAgent's legacy Profile-wire import path still validates those fields.
- **ARCHITECTURE INVARIANT:** UnityAgent remains the only Control Plane. Runtime route selection, capability resolution, current environment facts and execution do not belong to Hub data.
- **IMPLEMENTED CHANGE:** The registry no longer specifies `resolution.phase_order`. UnityAgent owns the algorithm. The manifest still declares required activation facts and fail-closed behavior.
- **IMPLEMENTED CHANGE (Hub vNext):** Registry v2 is a Manifest index. Manifest v3 and the Snapshot omit `default_profile`, `runtime_profile`, Backend `primary`, and UnityAgent-specific Evidence producer fields. UnityAgent's adapter retains consumer-owned Runtime Profile values.
- **IMPLEMENTED CHANGE (Hub vNext):** Hub validation permits overlapping active Capability declarations. UnityAgent's Import Gate enforces the current one-profile-per-capability limitation.

## Backend extraction gate

The current co-location is a documented transition exception, not Hub execution authority. The Artist package, CLI, tests, scripts, backend-specific skills, `VERSION`, `CHANGELOG.md`, `RELEASE_NOTES.md`, and release workflows follow the Artist product lifecycle. The Hub contract workflow is already separate from Artist release workflows. Physical extraction is deferred until the version/tag owner, published artifacts, installer URLs, UnityAgent Provider references, manifest references, fixtures and external consumers have a compatible migration path. A new repository is not required if this ownership boundary remains explicit.

## Legacy detachment gate

The published annotated tag `v1.1.1` points to commit `ea437f11bcf5b46b6a7575f9d2f9b81a9c02da7c` and remains unchanged. The active release validator still requires a file under `Legacy/`; detachment is therefore deferred. Historical source can be inspected at the immutable tag after that validator is migrated, without rewriting history or moving the tag.

## Support status

The current manifest and support matrix contain only Unity 6.x+ Built-in, URP and HDRP. Unity 2022.3 gate and bounded fallback records remain historical evidence and do not establish current production support.
