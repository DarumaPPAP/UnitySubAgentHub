# Specialist Expansion: Legacy Capability Salvage Audit

## 結論と調査範囲

**FACT（Source inventory）:** `Legacy/MyUnityMCP-1.1.1/Package/Editor/**/*.cs` の `[McpForUnityTool]` 宣言は77件で、名前の重複はありません。内訳はGraphics 32、Agent 10、WorldCreator 3、Profiler 8、Addressables 4、UI 5、Animation 5、Audio 5、Cinematic 5です。`Tests/Hub/test_legacy_salvage.py` がSourceと[全件Matrix](legacy-capability-salvage.csv)の一致を検査します。

**FACT（現行依存）:** UnityAgentの `Runtime/Tooling/provider_registry.yaml` は `myunitymcp` Providerを登録し、`Runtime/Tooling/Providers/MyUnityMcp/capability_mapper.py` はLegacy名のToolを選択します。従って旧Tool宣言が存在することと、独立した後継実装が存在することは同義ではありません。Legacyの削除条件「active Legacy path dependencies = 0」は現在未成立です。

**AUDIT DECISION:** 50件をPORT、12件をKNOWLEDGE、15件をRETIREと分類しました。REPLACEDは0件です。これは「現行AdapterがLegacy Tool名を利用している」状態を、置換済みと誤認しない保守的な分類です。PORTは実装完了を意味しません。全PORTの実装・Eval・置換Evidenceは未完了です。

| Decision | 件数 | 意味 |
|---|---:|---|
| REPLACED | 0 | 独立した後継実装と動作Evidenceを確認済み |
| PORT | 50 | 有用なCapabilityを適切なOwnerへ回収する候補 |
| KNOWLEDGE | 12 | Skill、Policy、Context rule、静的Contractへ翻訳する候補 |
| RETIRE | 15 | 旧Control Plane、実行Frontend、内部Status等を移植しない |
| UNRESOLVED | 0 | 分類自体が未決定のTool |

## Owner判断

- GraphicsのVisual Direction、Scene演出、Lighting、Capture、BakeはArtist側のCapability候補です。RenderGraph、Shaderの実装正当性をGraphicsSubAgentへ誤配分しません。現行UnityArtistCLIの高水準コマンドは確認できますが、旧32操作との完全な意味・入力・Evidence互換は未検証です。
- Profiler 8件はPerformanceSubAgentの計測Loopと決定論的Capture Toolへ回収する候補です。ProfilerSubAgentは作りません。Editor計測値をTarget Device Evidenceへ昇格しません。
- AddressablesはContentのSkill / Tool Pilotへ。最初はRead-only AnalyzeとPlanを対象とし、旧 `apply_entry` の自動移植はしません。
- UI、Animation、AudioSourceの既存Scene操作は、Import最適化のContent Domainと混同せず、UnityAgentの決定論的Tool候補とします。CinematicはArtistの既存Timeline契約との意味差を検証します。
- Agent 10件は旧Control Plane入口なのでRETIRE候補です。UnityAgentのOrchestration、Runtime、Persistence、Operationsで責務を保持し、旧MCP FrontendをCanonical pathへ復活させません。
- WorldCreatorの `compile_workflow` と `create_review_handoff` はPlanningとHuman Reviewの知識として回収候補です。`world.start_preflight` は旧UnityAgentMcpRuntimeへのExecution FrontendなのでRETIREです。WorldCreatorからSubAgentを直接Dispatchしません。

## Safety invariant照合

| Legacy rule | 現行確認先 | 判定 |
|---|---|---|
| read-only prepare | `Runtime/Tooling/Providers/MyUnityMcp/myunitymcp_provider.py` | Legacy Adapterでは確認。新Tool共通Contractへの移管は未検証 |
| expected revision for mutation | `Runtime/Contracts/mutation-evidence.schema.yaml`; MyUnityMcp Provider | 現行のMutation Evidenceに存在。各PORT先では再検証が必要 |
| approval token for mutation | `Policy/Approval/approval-policy.yaml`; `Runtime/Guardrails/tool_runtime_guard.py` | PolicyとGuardに存在。新Toolの実行経路で要E2E |
| one-time plan | MyUnityMcp Provider / Legacy source | Legacy固有。新ToolではPlan再利用拒否を個別検証 |
| automatic save prohibited | `Policy/Security/tool-trust.yaml` | Policyに存在。新Backendの実動作を要検証 |
| automatic full bake prohibited | Legacy `Catalog/production-surface-contract.yaml` | 現行全Providerでの一律適用は未確認。Bake追加時に明示Gateを要する |
| generic serialized property mutation prohibited | Legacy contract | 新Toolで型付きAllowlistを確認するまで移管済みとしない |
| silent fallback prohibited | `Policy/Security/tool-trust.yaml`; `Runtime/Permissions/mcp-activation.yaml` | Policyに存在。ToolBrokerの失敗伝播を要検証 |
| automatic visual acceptance prohibited | `Policy/Approval/approval-policy.yaml` | Human Review要求を確認。Visual E2Eは未実施 |
| automatic execution resume prohibited | Legacy contract | 新ExecutionモデルのResume policyを別途監査する |

この表は静的なコード・Contract照合です。Unity Editor、Player、Target Deviceでの動作成功を示しません。

## Legacy detachment gate

- [x] 77 ToolをSourceから再Inventoryし、全件分類
- [ ] PORT完了または明示的な機能別延期判断
- [ ] KNOWLEDGE移管完了
- [ ] REPLACEDの動作Evidence整備
- [ ] RETIRE後の実行経路切替検証
- [ ] active Legacy path dependencies = 0
- [x] Legacy sourceと公開履歴を保持

**判定:** Legacy Detachmentは禁止。旧MCP Transport、AutoRegister、Unity 2022.3対応は新Architectureに持ち込まない。
