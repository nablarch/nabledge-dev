**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加する設定が標準的な方法。JSP カスタムタグを使っている場合は nonce 生成も合わせて有効にする。

**根拠**:

① **固定ポリシーを設定する場合**（最もシンプルな方法）
`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定する。（`component/handlers/handlers-secure_handler.json:s7`）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'" />
</component>
```
これにより `Content-Security-Policy: default-src 'self'` ヘッダがレスポンスに付与される。

② **nonce を使う場合**（JSP カスタムタグ利用時は必須）
Nablarch のカスタムタグは一部 JavaScript を出力するため、nonce を使った対応が必要。`SecureHandler` の `generateCspNonce` を `true` にし、`policy` のプレースホルダー `$cspNonceSource$` に自動置換させる。（`component/handlers/handlers-secure_handler.json:s8`）

```xml
<property name="generateCspNonce" value="true" />
<!-- policy 例 -->
<property name="policy" value="default-src 'self' '$cspNonceSource$'" />
```
nonce はリクエストごとに生成され、カスタムタグが生成する `<script>` 要素に自動で `nonce` 属性がセットされる。（`component/libraries/libraries-tag.json:s9`）

③ **まず report-only で動作確認したい場合**
`ContentSecurityPolicyHeader` の `reportOnly` を `true` にすると `Content-Security-Policy-Report-Only` ヘッダになり、ブロックせずに違反レポートだけ収集できる。（`component/handlers/handlers-secure_handler.json:s9`）

**注意点**:
- Nablarch の CSP 対応は **nonce ベース**。nonce は HTML に埋め込まれるため、JSP 生成の HTML はリクエストごとに変化する（キャッシュに注意）。（`component/libraries/libraries-tag.json:s9`）
- カスタムタグを使う場合、`generateCspNonce` なしで `script-src 'unsafe-inline'` を許可するアプローチは非推奨。セキュアハンドラの nonce 機能と組み合わせることが前提の設計。（`component/handlers/handlers-secure_handler.json:s6`）
- まず `reportOnly: true` で本番同様の環境で違反を収集し、ポリシーを調整してから `false` に切り替えるのが安全な導入手順。

参照: `component/handlers/handlers-secure_handler.json:s6`, `component/handlers/handlers-secure_handler.json:s7`, `component/handlers/handlers-secure_handler.json:s8`, `component/handlers/handlers-secure_handler.json:s9`, `component/libraries/libraries-tag.json:s9`