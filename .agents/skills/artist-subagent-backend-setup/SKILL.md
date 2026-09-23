---
name: artist-subagent-backend-setup
description: Diagnose or explicitly install the optional ArtistSubAgent backend without turning setup into automatic capability resolution.
---

# ArtistSubAgent backend setup

ArtistSubAgent is optional. UnityAgent must exclude it from resolution while the backend/package/project binding requirements are not satisfied. Capability resolution must never auto-install it.

When the user explicitly requests setup for UnityAgent integration, enter through the UnityAgent Control Plane. Use an explicit Unity Project root and request only the `unity_artist_cli` backend product. Do not invoke the backend installer directly from this skill.

For a project, use an explicit path and machine-readable output:

```text
unity-agent doctor --product unity_artist_cli --project-path <project> --format json --non-interactive
unity-agent setup --operation plan --product unity_artist_cli --project-path <project> --format json --non-interactive > approved-plan.json
unity-agent setup --operation apply --product unity_artist_cli --expected-plan-id <plan_id> --approval-ref <approval_ref> --approved-plan approved-plan.json --project-path <project> --format json --non-interactive
unity-agent doctor --product unity_artist_cli --project-path <project> --format json --non-interactive
```

Present the exact plan before approval; apply only that plan and retain its InstallReceipt and Evidence. If the Control Plane is unavailable, report setup as blocked. Backend `unity artist version` and `unity artist capabilities` can provide additional read-only diagnostics, but cannot replace UnityAgent approval or activation checks. After setup, re-observe backend availability, project binding, package installation and Pipeline reachability. Only then may UnityAgent treat ArtistSubAgent as eligible.

Do not auto-install an Editor, bypass a Unity license, silently switch transports, or present the backend as a standalone Codex agent/plugin.
