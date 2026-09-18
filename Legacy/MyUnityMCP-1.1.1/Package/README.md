# MyUnityMCP v1.1.1 — Legacy Package

> このREADMEは`Legacy/MyUnityMCP-1.1.1/Package/`に保管された旧製品の記録です。現行UnityAgentのArchitecture、UnitySubAgentHubのHub Contract、ArtistSubAgentのBackend APIとして扱わないでください。

MyUnityMCP v1.1.1は、旧Unity Editor-onlyのMCP Packageです。旧UnityAgentMCP Control Planeから複数DomainのEditor WorkflowをOrchestrationする構成を記録しています。この旧Control Planeモデルは、現在の「UnityAgentだけがControl Plane、HubはMetadata Registry」という責務分離とは別の設計です。

## 保存されているRelease Surface

このArchiveのRelease記録では、Unity 6000.0以上向けの77 Tool Editor Surfaceを定義しています。

| Domain | Tool数 |
|---|---:|
| Graphics | 32 |
| Agent | 10 |
| WorldCreator | 3 |
| Profiler | 8 |
| Addressables | 4 |
| UI | 5 |
| Animation | 5 |
| Audio | 5 |
| Cinematic | 5 |

- 全Toolは`AutoRegister = false`。
- 旧AgentがUnity APIを直接Mutationしない境界を採用しています。
- AddressablesはOptional Packageとして扱い、未導入時の自動導入を禁止します。
- Addressables Content Build、Build Domain、MovieCreator Runtime、LiveCreator Runtimeはこのv1.1.1 Surfaceの対象外です。

これらの項目は旧Release Surfaceの説明であり、現在のArtistSubAgent Resolver候補やUnityAgent Provider一覧を表しません。

## Historical verification record

Archiveに記録されたv1.1.0 Unity 6000.7.0a2 Direct Editor Evidence、v1.1.1 Release CandidateのUnity 6000.0.75f1 EditMode / Compile / NUnit / Production Tool Discovery、Unity 6000.4.12f1 / 6000.5.5f1 Compatibility Matrixを参照できます。GameCI imageが利用できなかったUnity 6000.7 canary、Addressables Positive Backend Matrix、External Transport Disconnect / Reconnect、Target Deviceは未検証として記録されています。これは当時のRelease Evidenceであり、現在の環境に対する新しい検証結果ではありません。

旧導入情報は[Legacy Installation](Documentation~/installation.md)、Tool一覧は[Tool Reference](Documentation~/tool-reference.md)、旧Surface Evidenceは[Production Surface](Documentation~/production-surface.md)を参照してください。
