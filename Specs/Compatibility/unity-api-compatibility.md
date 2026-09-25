# UnityArtistCLI Unity API Compatibility

UnityArtistCLI maintains one compatibility boundary for the four supported release rows. It does not create a patch source fork for every Unity patch version.

## Buckets

The maintenance buckets are `BASE`, `UNITY_6000_4`, `UNITY_6000_5`, and `UNITY_6000_7`. Unity 6.6 changes roll into the `UNITY_6000_7` bucket. Confirmed API facts and planned breaking changes are separate in the compatibility record.

The current implementation is `Packages/com.darumappap.unity-artist/Editor/Compatibility/ArtistCompatibility.cs`; its EditMode coverage is `Packages/com.darumappap.unity-artist/Tests/Editor/ArtistCompatibilityTests.cs`. These files change together for compatibility-sensitive work and both carry Unity `.meta` files.

## Adapter policy

- Built-in uses the common `BASE` Editor API adapter on Unity 6.x+. Unity 2022.3 is not current production support.
- URP and HDRP use native Unity 6 adapters only.
- All Unity 2022.3 pipelines are unsupported and must be rejected before mutation.
- Unity 2023 and URP 14–16 are outside the formal release matrix.
- Package API availability is checked from both Unity version and package version; Editor version alone is not evidence.
- No generic version-specific fallback, serialized raw mutation, or arbitrary evaluation is permitted. Historical bounded batch evidence is retained but does not define current support.

## Gate evidence

Unity 6.x+ uses the official Unity CLI for command automation and Unity Pipeline for connected Editor commands. Unity 2022.3 historical Pipeline gate and bounded batch evidence are archived observations, not active fallback eligibility.
