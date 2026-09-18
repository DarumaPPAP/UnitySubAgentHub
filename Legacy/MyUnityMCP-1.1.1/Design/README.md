# Historical MyUnityMCP Design Assets

このREADMEは`Legacy/MyUnityMCP-1.1.1/Design/`に保存された、旧MyUnityMCP v1.1.1時点のDesign Assetだけを説明します。ここにある案は、UnitySubAgentHubや現在のUnityAgentへ昇格済みの仕様ではありません。

このLegacy Subtree内では、`Packages/`が旧Unity Package、`Catalog/`が当時のMCP Tool Contract、`Specs/`が当時のPackage仕様、`Tests/`が当時の検証を表します。これらのPathはArchiveの文脈で読み、現在のHubのSource of Truthと混同しないでください。

## 配置方針

`Design/`には、当時未実装だったControl Plane構想、Domain、Creator Workflowを置きます。Design Assetの存在は、機能の実装済み・利用可能を意味しません。

- 旧実行Package: `Legacy/MyUnityMCP-1.1.1/Package/`
- 旧MCP Catalog / Capability Contract: `Legacy/MyUnityMCP-1.1.1/Catalog/`
- 旧Technical Specs: `Legacy/MyUnityMCP-1.1.1/Specs/`
- 将来構想: この`Design/`
- 当時の履歴: Git historyとimmutable Release Tag

このArchive内のDesignを実装へ昇格する場合、旧製品ではPackage / Catalog / Test / Documentation / Current Spec / Release Contractを同一変更で更新する必要がありました。現在のSubAgent登録手順は[Hub Design Records](../../../Design/README.md)を参照してください。

公開済みのMyUnityMCP Tagは変更しません。
