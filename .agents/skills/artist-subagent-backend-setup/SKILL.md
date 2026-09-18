---
name: artist-subagent-backend-setup
description: Diagnose or explicitly install the optional ArtistSubAgent backend without turning setup into automatic capability resolution.
---

# ArtistSubAgent backend setup

ArtistSubAgent is optional. UnityAgent must exclude it from resolution while the backend/package/project binding requirements are not satisfied. Capability resolution must never auto-install it.

When the user explicitly requests setup, verify the backend with the official Unity CLI first. Check `unity --version`, then `unity artist version --format json`. The compatibility backend executable is `unity-artist`.

For a project, use an explicit path and machine-readable output:

```text
unity artist install --project-path <project> --format json --non-interactive
unity artist doctor --project-path <project> --format json --non-interactive
unity artist capabilities --project-path <project> --format json --non-interactive
```

After setup, re-observe backend availability, project binding, package installation and Pipeline reachability. Only then may UnityAgent treat ArtistSubAgent as eligible.

Do not auto-install an Editor, bypass a Unity license, silently switch transports, or present the backend as a standalone Codex agent/plugin.
