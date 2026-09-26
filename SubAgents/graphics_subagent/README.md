# GraphicsSubAgent Read-only 候補契約

`contracts/capability-contracts.yaml` は Hub 登録前の候補契約です。Registry と Production Snapshot には含めません。UnityAgent の Pilot Profile は明示的な Pilot 指定がある場合だけ評価対象になります。実 Unity Project の A/B/C 評価、Editor / Player / Target Device Evidence は `NOT_EVALUATED_RUNTIME` です。Provider は UnityAgent ToolBroker が実在する読み取り・観測 Tool から解決し、GraphicsSubAgent は直接選びません。
