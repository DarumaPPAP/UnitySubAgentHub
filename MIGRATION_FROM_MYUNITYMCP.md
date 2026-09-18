# Migration from MyUnityMCP v1.1.1

The repository now maintains the UnitySubAgentHub registry and contract surface. ArtistSubAgent is its first registered specialist; its existing CLI and Unity package remain the implementation backend during this transition. The published MyUnityMCP v1.1.1 tag and `Legacy/MyUnityMCP-1.1.1/` remain unchanged as migration references.

| Responsibility | Current owner |
|---|---|
| Specialist identity, lifecycle, compatibility, dependencies, capabilities, backend and evidence references | `SubAgents/<id>/manifest.yaml` |
| Registry indexing and shared fail-closed contract | `Registry/subagents.yaml` |
| Manifest and registry shape | `Schemas/` |
| Goal, policy, approval, environment discovery, binding, routing, execution, loop/fallback and evidence | UnityAgent |
| LookDev, mood, lighting, environment, camera, Timeline, and Cinemachine | ArtistSubAgent |
| Current Artist implementation transport | `unity_artist_cli` backend using Official Unity CLI / Unity Pipeline |
| Old MCP bridge and 77-tool surface | Legacy only; production-disabled |

Every specialist is optional. Registration does not mean installation or readiness. UnityAgent excludes an uninstalled, incompatible, unbound, unavailable, false, or unknown specialist before ranking. Capability resolution never installs a specialist; setup is a separate explicit request.

The new Artist backend has no dependency on `com.coplaydev.unity-mcp`. Its commands are discovered through Unity Pipeline `[CliCommand]` methods and invoked by the current backend adapter. `unity_artist_cli` is an implementation identity and does not replace `artist_subagent` in capability routing.

See [UnitySubAgentHub Architecture](Design/subagent-hub-architecture.md), the [ArtistSubAgent manifest](SubAgents/artist_subagent/manifest.yaml), and the [backend behavior specification](Specs/ArtistSubAgent/spec.md) for the current contract.
