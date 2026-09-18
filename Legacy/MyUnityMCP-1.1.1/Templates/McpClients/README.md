# Legacy MyUnityMCP MCP Client Templates

ここにある設定例は、`Legacy/MyUnityMCP-1.1.1/`の旧MCP Bridgeに接続するClient Templateです。現在のArtistSubAgentやUnityAgent Codex Pluginの接続設定ではありません。

旧Unity Packageに`Window > MCP for Unity`による自動設定があるClientでは、まずその方法を使います。ここにあるTemplateは、自動検出されないHTTP対応Client向けのFallbackです。

`<UNITY_MCP_HTTP_URL>`を旧Bridge UIに表示されたEndpointへ置き換えます。Clientごとの設定Schemaは異なるため、各Clientの公式仕様を確認してください。`recommended-readonly-allowlist.json`は設定ファイルではなく、旧Bridgeで最初に公開するToolの推奨一覧です。
