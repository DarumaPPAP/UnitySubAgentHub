# UnitySubAgentHub Architecture

## Authority

UnitySubAgentHubはOptional Specialistの静的なRegistry、Manifest、Schema、Contract参照とValidationを所有します。UnityAgentが唯一のControl Planeです。

| Hub owns | UnityAgent owns |
|---|---|
| Registry index、Specialist identity、Lifecycle | User request routing、Task Fingerprint、CapabilityRequest |
| 静的Capability、Compatibility、Dependency、Backend参照 | Environment discovery、Project binding、Capability / Provider resolution |
| Activation requirement、Evidence interface、Contract参照 | Policy、Approval、Execution、Retry / fallback、Persistence、Evidence normalization |
| Manifest / Snapshot schemaと検証 | 現在のProfile値、Import判断、Runtime Context、Setup |

HubのRegistryやSnapshotはInstall状態、Project状態、現在のPlatform、Provider health、選択済みSkill / Providerを表しません。RegistryからBackendを実行・Installしません。

## Canonical contracts

| Concern | Source |
|---|---|
| Registry index | `Registry/subagents.yaml` |
| Specialist静的契約 | `SubAgents/<id>/manifest.yaml` |
| Registry / Manifest / Snapshot schema | `Schemas/` |
| Specialist固有の詳細契約 | Manifestから参照されるファイル |
| Runtime ProfileとImport Adapter | UnityAgent |

Registry v2はManifest Pathのみを索引化します。Manifest v3はIdentity、Lifecycle、Optional Installation、Activation、Capabilities、対応するUnity Version / Render Pipelineの組、Dependencies、Backend identities、Evidence requirementsを宣言します。`audience`、`goal_type`、`primary_capability`、既定Profile、特定TaskのCamera GUID、Approval範囲はHubの契約に含めません。

## Lifecycle and eligibility

`active`は新規選出の候補です。`deprecated`、`retired`、`revoked`は履歴としてManifestとSnapshotに残せますが、新規選出から除外します。Manifestはrequired activation factsとfalse / unknown時の除外を宣言します。UnityAgentが現在のFactを観測し、判定順序とRankingを決めます。未導入、非互換、未Bind、利用不可、false、unknownを成功と扱いません。Setupは明示的な別操作です。

## Snapshot and import boundary

`Tests/Hub/export_agent_snapshot.py`は登録されたManifestを`subagent_catalog_snapshot` v1として出力します。各EntryはRepository相対の`manifest_ref`と静的な`manifest`を持ちます。ExporterはHub SchemaとManifest Schemaで出力を検証します。Hub CIは`Hub-SubAgent-Catalog-Snapshot`を公開します。

```text
Hub Manifest → Hub Snapshot → UnityAgent Offline Import Adapter → UnityAgent Runtime Catalog
```

SnapshotはUnityAgentの`SubAgentProfileCatalog` wire shapeではありません。UnityAgentのAdapterはSnapshotのbytes / digest、Identity、Provider、Capability、Activation、Evidenceを確認し、UnityAgent側の`audience`、`goal_type`、`primary_capability`、既定Profile、Reference scope / approval、Evidence producerを保持したImport Planを作ります。新しいSpecialistにConsumer固有Profileがない場合は自動推測せず明示的なImport Migrationを要求します。Artifactの公開だけではUnityAgent Catalogを変更しません。

Hub ValidationはManifestとしての合法性を判定します。例えば複数のactive Specialistが同じCapabilityを宣言しても静的契約としては合法です。現行UnityAgentが一意に解決できない場合、そのConsumer制約はUnityAgent Import Gateが拒否します。Hubは現在のUnityAgent Resolver制約をRegistryの汎用規則にしません。

Hub ManifestはRuntime Context値やTaskごとのSkill選択を所有しません。Context ContractやSkill参照を追加する場合も静的な受入契約と発見用Metadataに限り、既存のUnityAgent Context Assemblyと重複させません。

## Backend ownership

`artist_subagent`はSpecialist identity、`unity_artist_cli`はBackend identityです。Artist Package、CLI、Installer、Compatibility Tests、Release workflows、Backend固有SkillsとVersionはArtist Backend Productの責務です。現在は移行例外として同一Repositoryにありますが、Hub CIはBackend実行を必要としません。配布URLとRelease tagをUnityAgent Installerが参照しているため、物理分離の条件は[Authority cleanup audit](authority-cleanup-audit.md)に記録します。

## Add, deprecate and retire a specialist

1. `Schemas/subagent-manifest.schema.json`に適合する`SubAgents/<id>/manifest.yaml`を作成します。IdentityとBackend IDを分け、Optional Install、`auto_install: false`、required dependency gates、対応Target組、Evidence interfaceを宣言します。
2. Manifest PathだけをRegistryに追加し、`python Tests/Hub/validate_registry.py`、Hub Unit Tests、Snapshot exportを実行します。
3. UnityAgentが新しいCapability semanticsを扱えるか別に確認します。Consumer Profileが必要ならUnityAgent側でImport Migrationを実施します。
4. 廃止時はLifecycleを`deprecated`、`retired`または`revoked`へ変更します。既存利用・配布URL・Consumer参照を監査し、履歴が不要になるまでIdentityを再利用しません。

`Legacy/MyUnityMCP-1.1.1/`は現在のHubまたはBackend Runtimeではありません。現行Release Validatorが一部を参照するため、参照を移行するまでmainからの除去を保留します。公開TagとGit履歴は変更しません。
