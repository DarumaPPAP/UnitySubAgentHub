# UnitySubAgentHub

UnitySubAgentHubは、Unity向けのOptional Specialist SubAgentを登録・管理・検証するためのRepositoryです。専門AgentごとのManifest、Registry、共通Schema、CI検証を提供します。**SubAgentの実行やユーザー要求のルーティングは担当しません。**

```text
User / Codex → UnityAgent（唯一のControl Plane）→ 条件を満たしたSubAgent → Backend
                                ↑
                      このHubのRegistry / Contract
```

Policy、Approval、環境検出、Project Binding、Capability解決、実行、Retry/Fallback、Evidence正規化はUnityAgentが担当します。Registryに登録されていることは、インストール済み・利用可能・実行可能であることを意味しません。

## 登録済みSubAgent

| Specialist | 正本ID | Backend ID | Lifecycle |
|---|---|---|---|
| ArtistSubAgent | `artist_subagent` | `unity_artist_cli` | `active` |

SpecialistとBackendのIDは別物です。Artist Backendの既存実装は移行中の互換性維持のため `Packages/` と `src/` に残していますが、Hub Registryから実行することはありません。

## 解決条件とインストール方針

すべてのSubAgentはOptionalです。UnityAgentは候補をランキングする前に、Lifecycle・インストール・互換性・Project Binding・Availability・Manifestの有効化条件を確認します。

```text
registered → discovered → installed → compatible → project_bound
           → available → eligible → ranked
```

新しいCapability解決の対象になるのは `active` のみです。未インストール、非互換、未Binding、Unavailable、条件が `false` または `unknown` のSubAgentは除外します。利用可能なProviderがなければ `unavailable` を返します。Capability解決時の自動インストールは禁止です。Setupはユーザーが別途明示的に要求する操作です。

## 正本の場所

- `Registry/subagents.yaml`: Manifestのパスを列挙するIndexと、共通のFail-Closed規則
- `SubAgents/<id>/manifest.yaml`: SpecialistのID、Lifecycle、任意インストール、Capability、互換性、依存条件、Backend参照、Evidence要件
- `Schemas/`: RegistryとManifestの共通Schema
- Manifestが参照する各Contract: Specialist固有の詳細仕様と受け入れ条件
- `Design/subagent-hub-architecture.md`: HubとUnityAgentの責任境界、Lifecycle、登録手順

現在のProject状態やインストール状況は実行時にUnityAgentが観測します。ManifestやRegistryへ環境固有の状態を記録しません。

## 新しいSubAgentの追加

1. `Schemas/subagent-manifest.schema.json` に従って `SubAgents/<id>/manifest.yaml` を作ります。
2. Optional導入、`auto_install: false`、Fail-Closed有効化条件、Capability、互換性、依存条件、Backend、Evidenceを定義します。
3. Manifestのパスだけを `Registry/subagents.yaml` に追加します。
4. 次を実行します。

   ```sh
   python Tests/Hub/validate_registry.py
   python -m unittest discover -s Tests/Hub -p 'test_*.py' -v
   ```

HubのWorkflowは全Manifestを検証し、Registryへの登録漏れも検出します。さらに現在UnityAgentが読むProfile形式のデータ専用Snapshotを生成し、`UnityAgent-SubAgent-Catalog-Snapshot` Artifactとして公開します。共通ContractとUnityAgentが理解できるProfile機能で表現できるSubAgentの登録に、UnityAgent本体のソース変更は必要ありません。未対応のCapability意味論を追加する場合はUnityAgent側の機能対応が先に必要です。

## 最初の登録Agent: ArtistSubAgent

Artistの操作ガイドは[こちら](SubAgents/artist_subagent/README.md)、詳細仕様は[ArtistSubAgent Spec](Specs/ArtistSubAgent/spec.md)、Backend動作契約は[backend-surface-contract.yaml](SubAgents/artist_subagent/contracts/backend-surface-contract.yaml)です。

既存のArtist CLI・Unity Editor・Release Workflowは引き続き維持します。`Legacy/MyUnityMCP-1.1.1/` は移行履歴として変更しません。
