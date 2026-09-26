# PerformanceSubAgent Read-only 候補契約

`contracts/capability-contracts.yaml` はHub登録前の静的候補契約です。Registry、Production Snapshot、Production Manifestには登録しません。Capabilityは`performance.analyze`のみで、計測の実行、Provider選択、変更適用、Approval、RoutingはUnityAgentが管理します。

PerformanceSubAgentは観測済みのCPU / GPU / Memory / GC等のEvidenceを解釈し、bottleneckの分類、仮説、必要な追加観測、Recommendationを返します。ShaderやRenderGraphの実装正当性はGraphicsSubAgentの領域です。Profiler、ProfilerRecorder、FrameTimingManager等は決定論的なMeasurement Tool Surfaceであり、Specialist Identityではありません。

HubはIdentity、Capability、Read-only、Compatibility、Evidence、Receipt境界を定義します。UnityAgentのCandidate Consumer ProfileがActivation、Context、Routeを定義し、本契約の固定fixtureと照合します。実Unity ProjectのCompile / Editor / Player / Target DeviceおよびLive A/B/Cは`NOT_EVALUATED_RUNTIME`です。
