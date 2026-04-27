**質問**: セキュリティ対策で Content Security Policy を有効にしたら、既存の JSP 画面で onclick= とか書いてるボタンが動かなくなった。JSP の書き方を変える必要がある？ 避けられない？

---

**結論**: Nablarch カスタムタグを使っている場合は、`SecureHandler` の nonce 生成を有効にすれば、タグ側が自動的に nonce 属性を埋め込むため **JSP の書き換えは不要**。`tag-form_tag` が `onclick` 属性の関数呼び出しを含めて script 要素にまとめ直し、nonce 属性が付与される。カスタムタグを使っていない（素の HTML で `onclick=` を書いている）部分については、`tag-csp_nonce_tag` で nonce 属性を手動付与するか、外部 JS に切り出す必要がある。 — `component/libraries/libraries-tag.json#s9`、`component/libraries/libraries-tag.json#s10`

**① CSP 対応の前提**
`SecureHandler` で nonce 生成を有効にし、`ContentSecurityPolicyHeader` に `$cspNonceSource$` プレースホルダーを含むポリシーを設定しておく必要がある。 — `component/handlers/handlers-secure_handler.json#s8`

**② カスタムタグ使用時の自動動作**
`SecureHandler` で nonce 生成が有効な場合、以下のように自動で動作が変化する:
- `tag-form_tag` が生成する JavaScript（`onclick` 属性の関数呼び出し含む）を `script` 要素にまとめ、nonce 属性にハンドラ生成の nonce を設定する。
- `tag-script_tag` が生成する `script` 要素の nonce 属性にハンドラ生成の nonce を設定する。
- `tag-csp_nonce_tag` でハンドラ生成の nonce を出力可能になる。 — `component/libraries/libraries-tag.json#s9`

**③ カスタムタグ使用時の注意**
Nablarch の CSP 対応は nonce を利用する。nonce は HTML に埋め込まれるため、**JSP から生成される HTML がリクエスト都度変化する**（キャッシュ設計に注意）。 — `component/libraries/libraries-tag.json#s9`

**④ インライン記述を外部ファイルへ移行できない場合**
既存コンテンツにインラインで記述されたスタイル・スクリプトがあり外部化が困難な場合は、`tag-csp_nonce_tag` を使って対象要素に nonce 属性を付与する:

```jsp
<style nonce="<n:cspNonce />">
  /* ... */
</style>
<!-- 出力: <style nonce="DhcnhD3khTMePgXwdayK9BsMqXjhguVV"> -->
```
- `tag-script_tag` で作った script 要素は、nonce 生成が有効なら nonce 属性が **自動付与**。script 要素に nonce を付けたい場合は `tag-csp_nonce_tag` ではなく `tag-script_tag` を使うことが推奨。
- Content-Security-Policy をレスポンスヘッダで設定できずに meta 要素で設定する場合は、`tag-csp_nonce_tag` の `sourceFormat` 属性を `true` にすると `nonce-[生成された nonce]` フォーマットで出力される。 — `component/libraries/libraries-tag.json#s10`
