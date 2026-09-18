# ArtistSubAgent Guide

ArtistSubAgentはUnity Visual Art / LookDev / Lighting / Environment / Camera / CinematicのOptional Specialistです。UnityAgentから委譲される専門Agentとして設計し、第二のControl Plane、独自Provider Registry、独立したCodex Pluginにはしません。

## Identity

| Concept | ID / Name |
|---|---|
| Specialist identity | `ArtistSubAgent` |
| Canonical runtime ID | `artist_subagent` |
| Backend ID | `unity_artist_cli` |
| Host executable | `unity-artist` |
| Unity Package ID | `com.darumappap.unity-artist` |

`artist_subagent`はManifestの`identity.id`、`unity_artist_cli`はBackendの`id`です。既存の`unity-artist` executable、`unity artist <command>` UX、Package、`UnityArtist` namespaceはBackend compatibility surfaceとして残ります。

Identity、Lifecycle、Optional Install、Activation Gates、Dependency、Compatibility、Backend参照、Evidenceの正本は[manifest.yaml](manifest.yaml)です。このGuideはBackendの既存CLIと操作範囲を説明します。

## Resolver-visible boundary

Manifestが現在宣言するCapability:

- `artist.camera.inspect`
- `artist.camera.refine`
- `visual.capture`

Backend CLIのLookDev、Cinematic、Lighting / Environment、Evaluation、Historyなどのコマンドが存在しても、それだけではUnityAgent Resolverの候補になりません。Manifestで公開され、かつUnityAgent RuntimeがそのCapability semanticsをサポートしている必要があります。

## Optional activation

登録済みでも、自動的に導入・実行可能とは限りません。UnityAgentは解決前に次のFactを観測します。

- Backend available
- 対応Unity Version / Render Pipeline
- 正確なProject Binding
- Package installed
- Pipeline reachable

falseまたはunknownは候補から除外します。Capability解決時の自動Installは禁止です。Userが別途Setupを要求した場合にだけInstallを行います。

### 現在のUnityAgent連携状態

UnitySubAgentHub CIはManifestからSnapshot Artifactを公開しますが、2026-09-18時点でUnityAgentはそれを自動取込しません。UnityAgent mainのReferenceImplementationはチェックイン済みの`unity_artist_cli` Profileを読み、Hubが発行する`artist_subagent` Snapshotは`activation`フィールドとProfile IDの差により直接読み込めません。Import Adapterと全環境Gateの接続が完了するまでは、このGuideのContractを現行Runtimeで解決可能だと解釈しないでください。

## Backend CLI

```text
unity artist help
unity-artist --help
unity artist version --format json
unity artist doctor --project-path <project> --format json --non-interactive
unity artist capabilities --project-path <project> --format json
unity artist install --project-path <project> --format json --non-interactive
unity artist inspect|plan|preview|apply|capture|evaluate|refine|cinematic|history ...
```

`unity artist help`はUnity CLI Pluginのhelp、`unity-artist --help`は単独Executableのhelpです。現在のUnity CLI betaは`unity artist --help`をPlugin Dispatch前にGlobal helpとして処理します。これは外部CLIの互換制約です。

Operational commandは明示的なProject Pathを受け取り、`human` / `json` / `ndjson`を出力します。Mutationの基本順序:

```text
Inspect → Plan → Exact Diff → Expected Revision
       → UnityAgent Approval → Apply → Evidence
```

ApplyはUndoを登録しますが、自動Saveしません。

## Support matrix

この表はBackendのテスト対象Version / Pipelineであり、Install済みやResolver適格性の保証ではありません。

| Unity | Pipeline | Tier | Backend transport |
|---|---|---|---|
| 2022.3 LTS | Built-in | primary | Official Unity CLI + Unity Pipeline |
| Unity 6.x+ | Built-in | primary | Official Unity CLI + Unity Pipeline |
| Unity 6.x+ | URP | primary | Official Unity CLI + Unity Pipeline |
| Unity 6.x+ | HDRP | primary | Official Unity CLI + Unity Pipeline |

2022.3 URP / HDRP、Unity 2023、URP 14–16は正式対応外です。2022.3 Built-inはOfficial CLI + Pipelineを先に検証します。現在の記録では全列挙版がUnity 6.0要件で失敗した場合に限り、固定`unity run`バッチ入口`UnityArtist.UnityArtistBatchCommands.Dispatch`を限定Fallbackとして使います。任意コード実行、MCP、汎用CRUD、自動Saveは許可しません。

## Verify

代表的なBackend / Contract検証:

```powershell
dotnet build src/UnityArtist.Cli/UnityArtist.Cli.csproj
python Tests/Release/verify_unity_artist_contract.py
python Tests/Compatibility/verify-unity-api-compatibility.py
python -m unittest Tests/Minimal/test_minimal_smoke_contract.py
python Tests/Compatibility/verify-primary-urp-evidence.py
```

`blocked_by_environment`は成功ではありません。Static Contract、CLI parser、unsupported preflight、Direct Editor、E2E Evidenceを区別して記録します。各EvidenceとFixtureは[Compatibility README](../../Tests/Compatibility/README.md)を参照してください。

## Migration and layout

旧MyUnityMCP v1.1.1は`Legacy/MyUnityMCP-1.1.1/`にArchiveされています。新しいBackend Surfaceに旧MCP Transportや`McpForUnityTool`を再導入しません。

```text
src/UnityArtist.Cli/                         # unity-artist Backend host
Packages/com.darumappap.unity-artist/        # Unity Editor Backend API
SubAgents/artist_subagent/manifest.yaml      # canonical specialist identity / gates
SubAgents/artist_subagent/contracts/         # backend and capability contracts
Tests/Compatibility/                         # backend matrix and evidence
.agents/skills/artist-subagent-*/            # repository-scoped specialist workflows
```

UnityAgent Repositoryが唯一の`unity-agent` Codex Pluginを配布します。このRepositoryにArtistSubAgent専用Codex Pluginはありません。
