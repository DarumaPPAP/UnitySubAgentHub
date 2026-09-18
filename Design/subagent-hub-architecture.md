# UnitySubAgentHub Architecture

## Purpose and authority

UnitySubAgentHub's Hub contract surface is data and validation for optional specialist SubAgents. It indexes each specialist's contract, validates the contract shape and cross references, and records lifecycle state. It does not provide a runtime, orchestrator, or request resolver.

The first Artist backend implementation remains co-located in this repository for compatibility during the transition. That source and its release tooling belong to the Artist backend; the Hub registry and validator do not dispatch or execute it.

UnityAgent is the only Control Plane. It owns policy, approval, environment discovery, project binding, compatibility checks, capability resolution, execution, fallback, retries, and evidence normalization. The Hub supplies metadata; UnityAgent decides whether a specialist can participate in a request.

## Sources of truth

| Concern | Canonical source |
|---|---|
| Registry index | `Registry/subagents.yaml` |
| Specialist identity, lifecycle, optional installation, capabilities, compatibility, dependencies, backends, evidence | `SubAgents/<id>/manifest.yaml` |
| Manifest and registry structure | `Schemas/` |
| Specialist-specific behavior and acceptance | Paths linked by the manifest |
| Resolution and execution policy | UnityAgent |

Registry entries contain only manifest paths. A registry entry does not assert that a specialist is installed, project-bound, compatible, or eligible.

## Eligibility contract

The lifecycle and environment checks are applied before ranking:

```text
registered → discovered → installed → compatible → project_bound
           → available → eligible → ranked
```

Only `active` lifecycle entries may be considered. `deprecated`, `retired`, and `revoked` entries are excluded from new capability resolution. A false or unknown installation, compatibility, project-binding, availability, or manifest activation check excludes the specialist. An unavailable capability returns `unavailable`; the Hub and UnityAgent never install a specialist to satisfy a request. Setup is a separate explicit user operation.

Each manifest declares its own environment gates. Runtime observations such as installed version, current project, package reachability, and backend health do not belong in a committed manifest or registry snapshot.

## Identity and backend separation

`identity.id` names the delegated specialist (for example, `artist_subagent`). Each backend has its own identifier (currently `unity_artist_cli`). The two identities must differ. A specialist may reference more than one backend, and backend implementation can change without changing the specialist identity or capability contract.

## Adding a specialist

1. Create `SubAgents/<id>/manifest.yaml` using `Schemas/subagent-manifest.schema.json`.
2. Declare optional installation and `auto_install: false`; list all activation checks and fail-closed behavior.
3. Declare resolver-visible capabilities, exact supported version/pipeline target pairs, dependencies, backend references, evidence requirements, and lifecycle. Do not encode compatibility as independent version and pipeline arrays when the support matrix excludes some combinations.
4. Add only the manifest path to `Registry/subagents.yaml`.
5. Run `python Tests/Hub/validate_registry.py` and `python -m unittest discover -s Tests/Hub -p 'test_*.py'`.
6. Add any specialist-specific contract tests and preserve its existing CI.

Registering a specialist is data-only. It must not require UnityAgent source changes as long as the manifest uses the shared contract and UnityAgent already supports the declared capability semantics.

`Tests/Hub/export_agent_snapshot.py` generates a data-only profile snapshot from active manifests in the form consumed by the current UnityAgent ReferenceImplementation. CI publishes it as `UnityAgent-SubAgent-Catalog-Snapshot`; UnityAgent source is not copied into or invoked by the Hub. The snapshot is an input artifact only and does not claim that a backend is installed, compatible, bound to the current project, or ready. UnityAgent checks those live gates before ranking. The current ReferenceImplementation does not yet emit the Artist profile's `unity_artist_cli.compatible` fact, so the Artist profile remains ineligible while that fact is unknown; do not remove this gate to make the profile appear available. The current UnityAgent profile resolver also requires exactly one profile for a capability, so the Hub validator rejects overlapping active runtime capability ids until UnityAgent supports ranking them.

The Artist manifest currently exposes only `artist.camera.inspect`, `artist.camera.refine`, and `visual.capture` to the snapshot. Its wider CLI commands and operation contracts are not resolver-visible profiles until explicit capability entries and a supported UnityAgent runtime profile are added.

## Boundaries

- Hub validation reads metadata and referenced contracts; it does not discover local installations or project state.
- Hub code must not run a specialist, resolve user requests, install packages, or mutate projects.
- Specialist backend code is implementation owned by that specialist and is not part of the Hub contract or validation runtime. The co-located Artist implementation is a transition exception in repository layout only.
- `Legacy/MyUnityMCP-1.1.1/` is immutable migration history and is outside this architecture change.
