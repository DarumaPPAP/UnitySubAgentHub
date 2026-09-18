# Artist Backend Compatibility Evidence

`Tests/Compatibility/`には、Artist BackendのUnity Version / Render Pipeline別のCompatibility Contract、Direct Editor Evidence、Live Smoke / E2E Evidenceを置きます。これはBackendの挙動証明であり、Hub Manifestの登録、Install済み状態、UnityAgent Resolver eligibilityを単独で証明するものではありません。

## Source of truth

- `support-matrix.yaml`: Backendの4行Support Matrix
- `production-editor-acceptance.yaml`: Direct Editor Evidence
- `production-validation-evidence.yaml`: Host / Static / E2E Evidence
- `release-verification.yaml`: Release Audit
- `cli-pipeline-gate-evidence.yaml`: Unity 2022.3のOfficial Pipeline Gate結果
- `verify-*-evidence.py`: 各Evidence ContractのValidator

Unity 6 URP / HDRP Primary Visual Scenarioは各対応Evidence YAMLとVerifierが管理します。EvidenceにはPipeline-native Volume、Before / After Capture、Needs-refine Review、Guarded Refinement、Accepted Final Reviewを含みます。PNGはFixture Artifactとして扱い、PathとSHA-256をEvidenceに記録します。

## 2022.3 Built-in gate

Official Unity CLI + Pipelineを最初の候補として検証します。記録されたHostではUnity 2022.3.22f1上でPipeline PackageがUnity 6.0以上を要求し、固定Built-in Fixtureへの限定Batch Fallbackを別Contractで検証しました。Gate failureなしの自動Fallbackは認めません。

## Live checks

最小接続Editor Smoke:

```powershell
python scripts/run_minimal_live_smoke.py --project-path .\TestProjects\UnityArtistVerification
```

準備済みURP / HDRP Fixtureを再利用する場合は`--reuse-scene`を使います。Host / CLI / read-only inspectの確認には次を使えます。

```powershell
.\scripts\verify-external-cli.ps1 -ProjectPath .\TestProjects\UnityArtistVerification-URP
```

これらのEvidenceは`artist_subagent` Manifestの全Activation Gateが満たされたことや、Hub SnapshotがUnityAgent Runtimeへ取り込まれたことを意味しません。Resolver eligibilityはUnityAgentが現在の環境とProjectを別途観測して判定します。
