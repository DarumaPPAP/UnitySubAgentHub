# UnitySubAgentHub

UnitySubAgentHubは、Unity開発向けの**Optional Specialist SubAgentのmetadata Hub**です。複数の専門AgentのIdentity、Lifecycle、Capability、Compatibility、Dependency、Backend、Evidence契約を登録・検証します。

**UnityAgentが唯一のControl Planeです。** HubはRegistry、Catalog、Manifest、Schema、ValidationとCI Artifact生成を担当し、ユーザー要求のRouting、Runtime、Orchestration、Install、実行は行いません。

## 責務の境界

| Component | Owns | Does not own |
|---|---|---|
| UnityAgent | Policy、Approval、環境観測、Project Binding、Capability Resolution、実行、Fallback / Retry、Evidence | ― |
| UnitySubAgentHub | Registry Index、SubAgent Manifest、共有Schema、Fail-Closed Validation、Catalog Snapshot生成 | Request Resolver、Runtime、Orchestrator、Installer、Backend Dispatch |
| Specialist Backend | Manifestが参照する専門操作の実装 | Control Plane、一般要求のRouting、独自Policy Authority |

Registry登録は、導入済み・互換・ProjectへBinding済み・利用可能・実行可能を意味しません。すべてのSubAgentはOptionalです。Resolutionを理由に自動Installしません。

## 現在登録されているSpecialist

| Specialist | Canonical ID | Backend ID | Lifecycle |
|---|---|---|---|
| ArtistSubAgent | `artist_subagent` | `unity_artist_cli` | `active` |

ArtistSubAgentは専門AgentのIdentityです。`unity_artist_cli`は現在の実装Backend ID、`unity-artist`はHost CLIのExecutable名、`com.darumappap.unity-artist`はUnity Package IDです。これらを同じIdentityとして扱いません。

現在ManifestがResolver向けに宣言するCapabilityは`artist.camera.inspect`、`artist.camera.refine`、`visual.capture`です。Backend CLIの全コマンドやContractに書かれた広い機能（LookDev、Cinematic、Lighting、Environment、Evaluation等）は、ManifestとUnityAgent Runtimeの両方で対応されるまでResolver候補ではありません。

## Fail-Closed eligibility

Eligibilityの確認はRankingより先です。

```text
registered → discovered → installed → compatible → project_bound
           → available → eligible → ranked
```

新しいCapability解決では`active` Lifecycleだけを対象にします。必須の環境事実がfalse、unknown、Unavailableの場合、Specialistを候補から除外します。Manifestは条件を宣言しますが、現在のProjectの状態は保持しません。UnityAgentが実行時に観測します。

ArtistSubAgentのActivation gates:

- `unity_artist_cli.available`
- `unity_artist_cli.compatible`
- `unity_artist_cli.project_bound`
- `unity_artist_cli.package_installed`
- `unity_artist_cli.pipeline_reachable`

条件を満たす候補がなければ`unavailable`を返します。Installは別途Userが明示したSetup操作です。

## Canonical files

- `Registry/subagents.yaml`: Manifest PathのIndexと共通Fail-Closed規則
- `SubAgents/<id>/manifest.yaml`: SpecialistのCanonical Contract
- `Schemas/`: Registry / Manifest Schema
- Manifestが参照する`contracts/`: 詳細なCapability、Backend、Evidence Contract
- `Design/subagent-hub-architecture.md`: Architectureと追加手順

`SubAgents/<id>/manifest.yaml`が各Specialist情報の正本です。RegistryはManifest Pathだけを列挙し、環境固有のInstall状態やProject Bindingを保存しません。

## UnityAgent Snapshotとの現在の境界

HubのCIはActive Manifestからデータ専用の`UnityAgent-SubAgent-Catalog-Snapshot` Artifactを生成・公開します。これはCI Outputであり、UnityAgent Runtimeへ自動同期・取込される経路ではありません。

2026-09-18時点のUnityAgent `main`は`Runtime/ReferenceImplementation/subagent-catalog.yaml`を`SubAgentProfileCatalog`で読み込みます。Hub Exporterが生成するSnapshotには`activation`フィールドが含まれますが、現行Profile Loaderは未知フィールドを拒否します。また、Hub SnapshotのProfile IDは`artist_subagent`、UnityAgentのチェックイン済み互換Profile IDは`unity_artist_cli`です。このため、Snapshotは現状そのまま実行時に読み込めません。両Repository間にData Adapter / Importerが必要です。

さらに、Artist Manifestは`unity_artist_cli.compatible`を必須Gateとしますが、現在のUnityAgent ReferenceImplementationはこのFactを出力しません。Runtime連携が実装されるまではunknownとしてFail-Closedにし、ArtistSubAgentを適格候補として表示しません。README上でArtifact公開をRuntime Integration済みと表現しないでください。

このRegistryを使うUnityAgent側のImport/Adapterを追加・変更するときは、SnapshotのSchema、Identity/Backend分離、全Activation Gateを両Repositoryで同時に検証してください。新しいCapability semanticsを追加する場合はUnityAgent Runtimeの対応も必要です。

## Specialist追加手順

1. `Schemas/subagent-manifest.schema.json`に従い`SubAgents/<id>/manifest.yaml`を作成します。
2. Optional Install、`auto_install: false`、Lifecycle、False / Unknown fail-closed gateを定義します。
3. Resolver-visible Capability、対応Unity Version / Render Pipelineの組み合わせ、Dependency、Backend、Evidence Contractを宣言します。
4. Manifest Pathを`Registry/subagents.yaml`へ登録します。
5. 次のValidationを実行します。

```sh
python Tests/Hub/validate_registry.py
python -m unittest discover -s Tests/Hub -p 'test_*.py' -v
python Tests/Hub/export_agent_snapshot.py --output /tmp/subagent-catalog.yaml
```

CIは全Manifest、重複Capability、Required Dependency Gate、Index Coverageなどを検証し、Snapshot Artifactを公開します。ArtifactはUnityAgentに取込済みであることを示しません。

## ArtistSubAgent

- [ArtistSubAgent Guide](SubAgents/artist_subagent/README.md)
- [Canonical Manifest](SubAgents/artist_subagent/manifest.yaml)
- [Hub Architecture](Design/subagent-hub-architecture.md)
- [Migration from MyUnityMCP](MIGRATION_FROM_MYUNITYMCP.md)

`Legacy/MyUnityMCP-1.1.1/`は旧MCP Packageの移行記録です。現在のHub RuntimeでもArtistSubAgent Backendでもありません。公開済みLegacy Tagは変更しません。

MIT License. See [LICENSE](LICENSE).
