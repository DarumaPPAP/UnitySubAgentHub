# ArtistSubAgent Backend Specification

## Product boundary

ArtistSubAgent is the optional Artist specialist selected by UnityAgent. It handles visual intent inspection and planning, mood/lookdev, lighting, environment, sky/fog/reflection/GI, camera/depth/continuity, Cinemachine/Timeline cinematic planning, capture, human evaluation, and linked refinement. It does not become a general Unity editor API or a second Control Plane.

The canonical Specialist identity, lifecycle, optional installation policy, capabilities, compatibility ranges, dependencies, activation gates, backend references, and evidence requirements are in the [ArtistSubAgent manifest](../../SubAgents/artist_subagent/manifest.yaml). The backend id `unity_artist_cli`, host executable `unity-artist`, command UX `unity artist`, UPM package `com.darumappap.unity-artist`, and C# namespace `UnityArtist` identify implementation compatibility surfaces; they are not the Specialist identity.

## Current UnityAgent resolver profile

The current snapshot exposes only `artist.camera.inspect`, `artist.camera.refine`, and `visual.capture`. The LookDev, cinematic, lighting/environment, evaluation, and other operations described in this backend specification are not independent Resolver candidates until the Hub manifest explicitly registers them and UnityAgent supports their runtime profile.

## Transport and layering

```text
UnityAgent CapabilityRequest
  → Runtime Guard / Policy / Approval / Mutation Scope
  → ArtistSubAgent eligibility / plan
  → Backend Provider Registry / Resolver / Dispatcher
  → unity_artist_cli backend adapter
  → unity-artist
  → official Unity CLI command
  → Unity Pipeline [CliCommand]
  → Unity Editor API
  → structured ProviderResult / Evidence
```

The adapter accepts typed argv only, always supplies an explicit project path, uses bounded cancellation, parses JSON only, and uses an allowlisted command map. It never calls arbitrary eval or chooses aesthetic intent.

Historical experiment (not current support): for Unity 2022.3 LTS + Built-in, the host probed the Official Unity CLI/Pipeline install first. Only the recorded Unity 6.0-or-later Pipeline compatibility failure selected the bounded `official_unity_cli_bounded_batch_fallback`: `unity run` invokes the fixed `UnityArtist.UnityArtistBatchCommands.Dispatch` method with base64-encoded structured JSON and a single JSON response file. The bridge reuses `ArtistSession`, allowlists the Artist commands, loads an exact scene, and does not auto-save or persist approval tokens. It is not a second Player Framework, MCP transport, dynamic-code executor, or generic Unity CRUD surface.

## Activation contract

ArtistSubAgent is optional and must never be auto-installed by capability resolution. Its canonical gates are listed in the [manifest](../../SubAgents/artist_subagent/manifest.yaml); backend availability, compatibility, explicit Project binding, Artist UPM package installation, and Pipeline reachability must all be observed true. False or unknown activation facts exclude ArtistSubAgent before ranking or execution. Setup is an explicit operation initiated by the user.

## Backend command contract

Required commands are `help`, `version`, `doctor`, `capabilities`, `install`, `inspect`, `plan`, `preview`, `apply`, `capture`, `evaluate`, `refine`, `history`; `cinematic` is the explicit Timeline/Cinemachine specialist extension. Operational commands support `--project-path`, `--format human|json|ndjson`, `--non-interactive`, and `--verbose`. `unity artist help` and standalone `unity-artist --help` are the supported help entrypoints; the Unity CLI beta's global `unity artist --help` form is host-intercepted before plugin dispatch and is tracked as an external compatibility limitation.

`version --format json` returns product, CLI version, package id, transport, and compatibility backend. `doctor` observes CLI, project, package, Pipeline, safe-mode, render-pipeline, Timeline, Cinemachine, and approval readiness. `capabilities` returns the formal matrix and observed capabilities.

## Visual safety lifecycle

```text
Inspect → Visual Intent → Exact Plan/Diff → Expected Revision
→ UnityAgent Approval → Apply → Undo/Evidence
→ Capture → Human Evaluate → Refine
```

Inspect/Plan/Preview are read-only. Apply requires `plan-id`, `expected-revision`, and an opaque UnityAgent approval token. It does not save the project. Capture produces a bundle reference and camera/look/lighting/plan metadata; capture is not acceptance. Evaluate requires a human decision: `accepted`, `rejected`, or `needs_refine`.

## Artist and cinematic surface

The semantic surface includes LookDev and visual direction, Lighting, Environment, Camera, Visual Capture, Visual Evaluation, Refine, Timeline, Cinemachine Shot, Activation, Signal/Marker, Control, Animation, Track/Clip/Binding inspection and bounded mutation. Generic Project/Scene Save/Test/Build/Play/Stop/Console operations are delegated to the official Unity CLI or existing UnityAgent providers.

## Support matrix

| Unity version | Pipeline | Adapter | Status |
|---|---|---|---|
| Unity 6.x+ | Built-in | `builtin_editor_api` | primary |
| Unity 6.x+ | URP | `urp_native_api` | primary |
| Unity 6.x+ | HDRP | `hdrp_native_api` | primary |

Current manifest lists only Unity 6.x+ Built-in, URP, and HDRP. All Unity 2022.3 pipelines are excluded from current support. Historic 2022.3 bounded batch Evidence is preserved for provenance, not active fallback eligibility.

## Error and terminal states

The ArtistSubAgent backend uses structured codes including `PROJECT_PATH_REQUIRED`, `UNITY_CLI_UNAVAILABLE`, `PIPELINE_INSTALL_FAILED`, `CAPABILITY_UNAVAILABLE`, `UNSUPPORTED_UNITY_VERSION`, `UNSUPPORTED_RENDER_PIPELINE_VERSION`, `STALE_REVISION`, `APPROVAL_REQUIRED`, `PLAN_ID_REQUIRED`, `CAMERA_NOT_FOUND`, `INVALID_REVIEW_DECISION`, `TIMEOUT`, and `ARTIST_PIPELINE_COMMAND_FAILED`.

Evidence artifact requirements and terminal states are declared by the [manifest](../../SubAgents/artist_subagent/manifest.yaml) and its linked release-verification contract. `implemented_unverified` is not a completion state. The 2022.3 bounded fixture uses `verified_for_fixture` inside its evidence record and is rolled up to the release audit separately from the remaining host-level limitations.
