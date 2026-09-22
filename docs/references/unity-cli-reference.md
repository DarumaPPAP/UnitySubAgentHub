# Unity CLI公式リファレンスの購読・監査基準

UnitySubAgentHubはRuntimeやBackendを実行しない。ここで管理するUnity CLI参照は、ArtistSubAgentのBackend／Compatibility／Evidence契約を更新する必要があるかを判断するための一次資料である。

## 正本資料

- [Unity CLI](https://docs.unity.com/en-us/unity-cli)
- [Unity CLIリファレンス](https://docs.unity.com/en-us/unity-cli/unity-cli-reference)
- [Unity CLIリリースノート](https://docs.unity.com/en-us/unity-cli/release-notes)
- [Unity Pipeline package](https://docs.unity.com/en-us/unity-production-pipeline/local-tools-cli/unity-pipeline-package)
- 機械検証用の監査契約: [`Tests/Compatibility/unity-cli-reference-audit.yaml`](../../Tests/Compatibility/unity-cli-reference-audit.yaml)

最終確認日: 2026-09-21  
公式資料上の最新CLIリリース: `1.0.0-beta.10`  
実機観測状態: `not_observed`

beta.10は公式資料で確認したリリース番号であり、HubまたはUnityAgentの検証環境で実行したCLIバージョンではない。既存のbeta.8受入証跡は過去のFixture検証として保持し、beta.10の実機結果へ置換しない。

## Hubの責務境界

- 公式CLIのcommandをRuntimeで呼び出さない。
- ArtistSubAgentの `unity_artist_cli` Backend identityとmanifestの宣言を管理する。
- UnityAgentが観測する `available`、`compatible`、`project_bound`、`pipeline_reachable` などの事実を捏造しない。
- 未導入・非互換・未bind・unknownを候補へ含めず、自動インストールもしない。
- CLI仕様変更がBackend surfaceやCompatibility matrixに影響するときだけ、UnityAgent側の実装PRと分離して契約を更新する。

## 監査対象

| 公式仕様 | Hubで確認する契約 |
|---|---|
| `unity version --format json` | Backendの対応条件やEvidenceのversion表現を更新する必要があるか。 |
| `unity commands --format json` | Artistの接続可能commandとHubの宣言を混同していないか。 |
| `unity pipeline` | Pipelineを一次経路とする宣言、Unity 2022.3のbounded fallback条件、no-auto-install境界。 |
| `unity test` の終了コード | Hubでは実行結果を生成せず、UnityAgentのProvider／Evidence契約への影響だけを記録する。 |

CLIは実験的仕様であり、実際にインストールされたCLIの `unity --help` が最終的なcommand/option authorityである。Hubのmanifestやregistryを公式資料の一覧だけで「installed」「compatible」「executable」と判定してはならない。
