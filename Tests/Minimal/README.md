# Unity 6 Built-in Minimal Live Smoke

`scripts/run_minimal_live_smoke.py`は、接続済みUnity 6 Built-in Editorに対するArtist Backendの最短E2E Smokeです。Disposable Fixtureに限定し、一般のProjectでのMutationやHub Snapshot Integrationを検証するものではありません。

## Preparation

Repository RootからFixtureにOfficial Unity PipelineをInstallし、Editorを開きます。

```powershell
unity pipeline install --project-path .\TestProjects\UnityArtistVerification --proxy-disable
unity open .\TestProjects\UnityArtistVerification --editor-version 6000.6.0f1 --non-interactive --no-banner --proxy-disable
python scripts/run_minimal_live_smoke.py
```

## Checks

SmokeはDefault Main Camera、Directional Light、Cubeだけの`Assets/MinimalSmoke.unity`を生成し、次を確認します。

1. Official Unity CLI / Pipeline経由でArtist supportを検出する
2. Plan / PreviewがRead-onlyでExact Diffを返す
3. Approval TokenなしではApplyを拒否し、Tokenありでは適用する
4. Mutation、Undo、未SaveをEvidenceへ記録する
5. 有効なPNG Captureを生成する
6. Evaluate / RefineのVisual loopを実行する
7. Session EvidenceをHistoryから取得する

これはSmokeでありRelease Matrixの代わりではありません。各結果は[Compatibility Contracts](../Compatibility/README.md)を参照してください。
