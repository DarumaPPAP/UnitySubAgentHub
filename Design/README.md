# Hub Design Records

`Design/`には、複数のOptional Specialist SubAgentを登録するUnitySubAgentHubのArchitecture ContractとDecision Recordを置きます。Hubの現行責務はmetadataのRegistry、Manifest、Schema、Validationです。

## Canonical records

- `Registry/subagents.yaml`: 登録ManifestのIndexとFail-Closed規則
- `SubAgents/<id>/manifest.yaml`: Specialist identity、lifecycle、installation、capability、compatibility、dependency、backend、evidence契約
- `Schemas/`: Registry / Manifestの共通Shape
- Manifestが参照するContract: Specialist固有の詳細仕様と受け入れ条件
- `subagent-hub-architecture.md`: HubとUnityAgentの責任境界
- `specialist-expansion-architecture.md`: Registered Specialist候補の境界とEval条件
- `legacy-capability-salvage-audit.md` / `legacy-capability-salvage.csv`: Legacy 77 ToolのSource inventory、分類、削除Gate

UnityAgentが唯一のControl Planeです。Hubの記録はSpecialistが導入済み、eligible、実行可能であることを示しません。HubはRuntime、Orchestrator、Request Resolver、Installerではありません。

## Legacyとの区別

`Legacy/MyUnityMCP-1.1.1/Design/`は旧MyUnityMCPの設計記録です。現在のHub ContractやUnityAgentのProduction Architectureとして読み替えないでください。
