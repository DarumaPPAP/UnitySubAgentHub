# UnitySubAgentHub Documentation Index

このIndexは、Hubの**Current Contract**とHistorical / Backend-specific資料を分離して読むための入口です。

## Current Hub contract

- [Repository README](../README.md)
- [Hub Architecture](architecture/subagent-hub-architecture.md)
- [Design Records](architecture/README.md)
- [Registry](../Hub/Registry/subagents.yaml)
- [Manifest / Snapshot Schemas](../Hub/Schemas)
- [Specialist Execution Admission](../Hub/specialist-execution-admission.yaml)

HubはRegistry / Manifest / Schema / Validationを所有します。Runtime resolution、Policy、Approval、Project binding、Execution、Retry、Evidence normalizationはUnityAgentが所有します。

## Registered specialists

| Specialist | Guide | Manifest |
|---|---|---|
| ArtistSubAgent | [Guide](../Hub/SubAgents/artist_subagent/README.md) | [Manifest](../Hub/SubAgents/artist_subagent/manifest.yaml) |
| GraphicsSubAgent | [Guide](../Hub/SubAgents/graphics_subagent/README.md) | [Manifest](../Hub/SubAgents/graphics_subagent/manifest.yaml) |
| WorldCreatorSubAgent | [Guide](../Hub/SubAgents/world_creator_subagent/README.md) | [Manifest](../Hub/SubAgents/world_creator_subagent/manifest.yaml) |
| PerformanceSubAgent | [Guide](../Hub/SubAgents/performance_subagent/README.md) | [Manifest](../Hub/SubAgents/performance_subagent/manifest.yaml) |

Current manifests are v5 and current exported Snapshot is v3.

## Backend-specific documentation

Artist backend implementationは移行上このRepositoryに同居していますが、Hub Runtimeではありません。

- [Artist Unity Package](../Packages/com.darumappap.artist-subagent/Documentation~/README.md)
- [ArtistSubAgent Specification](architecture/artist-subagent-spec.md)
- [Unity API Compatibility](references/unity-api-compatibility.md)
- [Compatibility Tests](../ci/compatibility/README.md)
- [Unity CI Windows / Linux 実行手順（日本語）](../ci/README.md)

## Historical / migration records

- [Migration from MyUnityMCP](migration/MIGRATION_FROM_MYUNITYMCP.md)
- `tests/fixtures/legacy/MyUnityMCP-v1.1.1/` + Git tag `v1.1.1` — frozen historical provenance / detachment evidence
- `docs/decisions/` — dated decisions
- `docs/architecture/legacy-capability-salvage-audit.md` — Legacy 77 Capabilityの回収・延期・削除Gate
- `ci/evidence/artist/historical/` — preserved historical records; current Editor validation is not_observed

Historical Unity 2022.3 EvidenceはCurrent Production Supportを意味しません。Current manifestsが宣言する対象はUnity 6.x+のBuilt-in / URP / HDRPです。

## Candidate baseline files

Graphics / WorldCreator / Performanceには、Production昇格前の比較用として `contracts/capability-contracts.yaml` が残っています。これらは `status: pilot_unregistered` を保持する**Historical baseline**です。

Current Production Contractは各Manifestの `capability_contract_ref` を参照してください。

## Maintenance rule

- Specialist追加・Lifecycle変更時はRegistry、Manifest、Schema、Hub Tests、READMEを同期する
- Backend追加とSpecialist追加を同一Identityとして扱わない
- Registry登録をinstalled / available / eligible / Production Verifiedと書かない
- Current docsへHistorical Support Matrixを混在させない
- MyUnityMCP v1.1.1のHistorical sourceはmainへ戻さず、Frozen FixtureとGit tag `v1.1.1` をprovenance正本として維持する

## Distribution boundary

Hubと個別SubAgentは独立Releaseを公開しません。UnityAgentが唯一のMarketplace / GitHub Release単位です。UnityAgent ReleaseはHubの固定commit SHAをpinしてSource/Contractを検証し、必要なBackend assetsとconsumer-neutral SnapshotをUnityAgent側のReleaseへ同梱します。
