**結論**: JSP で使っている `onclick=` が **Nablarch カスタムタグ（`n:form` 等）が生成したもの**であれば、SecureHandler の nonce 設定を有効にするだけで自動対応される。**手書きの `onclick=`（カスタムタグ外）**は、`<n:cspNonce />` を使ってnonce属性を付与するか、外部JSファイルに移行する必要がある。

---

**根拠**:

① SecureHandler の `generateCspNonce` を `true` にし、`ContentSecurityPolicyHeader` の `policy` に `$cspNonceSource$` プレースホルダーを含めることで CSP nonce 機能が有効になる。`$cspNonceSource$` はリクエストごとに `nonce-XXXXX` に置換されて `Content-Security-Policy` ヘッダに設定される。（`component/handlers/handlers-secure_handler.json:s8`）

② nonce 生成が有効な場合、**Nablarch カスタムタグの動作が自動変化**する。具体的には「onclick属性にサブミット用の関数呼び出しを設定するカスタムタグは、その内容を script 要素に出力するように変更する」とある。つまり `n:form` 等のカスタムタグが生成する onclick は、nonce 付き `<script>` ブロックに自動的に移動されるため JSP の書き換えは不要。（`component/handlers/handlers-secure_handler.json:s8`、`component/libraries/libraries-tag.json:s9`）

③ 一方、**既存コンテンツにインラインで記述されており外部ファイルへの移行が困難な場合**は、`<n:cspNonce />` カスタムタグを使って対象要素に nonce 属性を設定できる。例: `<script nonce="<n:cspNonce />">...</script>` のように記述する。（`component/libraries/libraries-tag.json:s10`）

---

**注意点**:
- Nablarch カスタムタグを経由しない**手書きの `onclick=` 属性**はブラウザに CSP でブロックされる。nonce を使うか外部 JS に移行する必要がある。
- nonce は **リクエストごとに新しく生成**されるため、HTML が毎回変わる点に留意（`component/libraries/libraries-tag.json:s9`）。
- `Content-Security-Policy` をレスポンスヘッダで設定できない場合は meta 要素で設定でき、その際は `<n:cspNonce sourceFormat="true" />` を使うと `nonce-XXXXX` フォーマットで出力される（`component/libraries/libraries-tag.json:s10`）。

参照: component/handlers/handlers-secure_handler.json:s8, component/libraries/libraries-tag.json:s9, component/libraries/libraries-tag.json:s10