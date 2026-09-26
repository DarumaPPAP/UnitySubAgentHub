# Registered Specialist Expansion: Architecture Foundation

## Status and authority

**ARCHITECTURE INVARIANT:** UnityAgent is the sole Control Plane. It owns Intent、Routing、Policy、Approval、Context Assembly、Specialist Selection、Provider Resolution、Retry / Loop Control、Persistence、Runtime State、Evidence Lifecycle. Hub owns static Specialist identity and contract only. `provider_id` identifies a Runtime Backend, never a Specialist.

**FACT:** Current Hub Registry contains ArtistSubAgent only. UnityAgent already has `rendering-incident`、`shader-change`、`renderer-feature-change`、`performance-experiment` routes and a Context Assembly. `Runtime/ReferenceImplementation/subagent-catalog.yaml` currently requires a Provider-bound Artist Profile. The Hub Manifest v4 still requires at least one Backend. Therefore WorldCreator Planning-only admission requires coordinated Hub Schema、UnityAgent Profile、Import Gate、Runtime、Evidence changes. A fake Provider is prohibited.

**PROPOSED CHANGE:** Graphics、Performance、WorldCreatorをRegistered Specialistとして順次評価し、ContentはSkill + deterministic ToolのPilotに留めます。新ManifestをEval前にProduction Registryへまとめて追加しません。

## Specialist admission gate

固定スコアは用いません。次の相違を定性的に記録します: Domain Ownership、Instructions、Tool Surface、Policy / Safety Boundary、Evidence Contract、Context Requirement、Approval / Mutation Boundary、独立したReasoning Loop。既存Skill + deterministic Toolで十分ならRegistered Specialistを追加しません。Task-scoped WorkerはHubへ登録せず、Compile failure、Shader failure、Package dependency、Test failure、Regression、Platform比較等の一時的な独立調査に使います。

| Specialist | Domain | 初期Capability | Mutation | Evidence |
|---|---|---|---|---|
| ArtistSubAgent | Visual direction / composition / aesthetics | 既存契約 | 既存の限定Scope | VisualとEditorの実測 |
| GraphicsSubAgent | Rendering implementation correctness / compatibility | `graphics.inspect`, `graphics.diagnose`, `graphics.validate` | Read-only Pilot。PatchはEval後 | Shader compile、RenderPass / RenderGraph観測、Variant、Pipeline compatibility |
| PerformanceSubAgent | Measurement / diagnosis / comparison / regression | `performance.capture`, `performance.analyze`, `performance.compare`, `performance.regression` | 原則Read-only | 計測条件・有効性・再計測比較 |
| WorldCreatorSubAgent | High-level world plan / work decomposition | `world.inspect`, `world.plan`, `world.review` | Planning-only | 構造化Plan、依存、Open Decisions、Required Evidence |
| ContentSubAgent | Import / Addressables候補 | Production未登録 | Skill + Tool Pilot | Importer Preview / Diff、Read-only Addressables Analyze |

## Routing and context

Graphicsは既存のRendering Routeを監査して再利用し、Performanceは `performance-experiment` を再利用します。WorldCreator用 `world-creation` は新Route候補ですが、FingerprintとTask ContractをUnityAgent正本に合わせます。Work Package内のDomainはRouting hintであり、UnityAgentの最終Decisionではありません。PlatformはContext / ConstraintでありSubAgentではありません。既存Context AssemblyのSkill、Project Facts、Platform Facts、Project Decisions、Platform Decisions、Task Factsを必要分だけ渡し、Generated → Transported → ReceivedのReceiptを維持します。

## WorldCreator planning boundary

WorldCreatorの出力はWorld Goal、Scene Scope、Environment Type、Visual Intent、Zones、Camera / Lighting / Content Requirements、Technical / Performance / Platform Constraints、Prohibited Changes、Acceptance Criteria、Work Packages、Dependencies、Required Evidence、Open Decisionsを含むStructured World Planです。Planの完全性と未決定事項の明示がWorldCreatorの成功条件です。Scene完成やVisual最終合格をWorldCreator単独の成功とはしません。UnityAgentがPlanを受けてRoute、Policy、Approval、Provider Resolution、Executionを行います。旧 `world.start_preflight → UnityAgentMcpRuntime.StartExecution` を直接移植しません。

## Evaluation and promotion

各候補を A: UnityAgentのみ、B: UnityAgent + Skill / Tool、C: UnityAgent + Specialist で比較します。Task success、Evidence completeness、誤前提、Tool選択誤り、Context bytes/tokens、不要Context、Tool calls、Retry、Approval違反、未裏付けClaim、Trace可読性、Latencyを記録します。GraphicsはRenderGraph / Shader / Variant / Depth / RendererFeature、PerformanceはCPU / GPU / GC / Memory / Before After / Target timing、WorldCreatorはDungeon / Boss Arena / Live Stage / Multi-zone / Existing Scene expansionを最低Caseとします。Skillが同等以上、Context分離効果なし、Routing ambiguity増加、Evidence差が小さい場合は昇格を見直します。

## Mutation and evidence

共通Mutation順序は Inspect → Plan → Exact Diff → Approval → Apply → Evidence。Read-only Pilotの診断結果をEditor / Player / Target Device成功へ昇格しません。Performance Captureにはmeasurement source、Unity version、Platform、Graphics API、capture mode、build type、scene、window、limitations、validityを記録します。GPU timing unavailable / zero、遅延、API制約を検証し、数値が返っただけでVerifiedにしません。Content AddressablesはAnalyzeから開始します。
