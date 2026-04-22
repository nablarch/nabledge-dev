**質問**: セキュリティ診断で Content Security Policy を入れろと言われた。Nablarch の Web 画面で CSP を有効にしたい。標準のやり方は？

---

**結論**: `SecureHandler`（セキュアハンドラ）の `generateCspNonce` プロパティを `true` にして nonce 生成を有効にし、`secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加してポリシーを設定する。Nablarch カスタムタグを使っている場合は、タグ側が自動的に nonce 属性を埋め込むように変更される。 — `processing-pattern/web-application/web-application-feature_details.json#s21`、`component/handlers/handlers-secure_handler.json#s6`

**① 構成要素**
`SecureHandler` + `ContentSecurityPolicyHeader` + Jakarta Server Pages カスタムタグの CSP 対応、の3つを組み合わせて CSP を有効にする。 — `component/handlers/handlers-secure_handler.json#s6`

**② 設定手順**
1. `SecureHandler` の `generateCspNonce` プロパティを `true` に設定する。
2. `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加する。
3. `ContentSecurityPolicyHeader` の `policy` にプレースホルダー `$cspNonceSource$` を含める。 — `component/handlers/handlers-secure_handler.json#s8`

**③ 設定例**
```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```
`$cspNonceSource$` は `nonce-[ハンドラで生成された nonce]` に置換される。 — `component/handlers/handlers-secure_handler.json#s8`

**④ カスタムタグ使用時の自動動作**
`SecureHandler` で nonce 生成を有効にすると、以下のようにカスタムタグの挙動が自動変化する:
- `tag-form_tag` が生成する JavaScript（`onclick` 属性の関数呼び出し含む）は `script` 要素にまとめられ、nonce 属性にハンドラ生成の nonce が設定される
- `tag-script_tag` が生成する `script` 要素の nonce 属性にハンドラ生成の nonce が設定される
- `tag-csp_nonce_tag` により任意の要素へ nonce を出力可能 — `component/libraries/libraries-tag.json#s9`

**注意点**
- nonce は HTML に埋め込まれるため、JSP から生成される HTML はリクエスト都度変化する。 — `component/libraries/libraries-tag.json#s9`
- nonce はリクエスト都度生成され、リクエストスコープに格納される。 — `component/handlers/handlers-secure_handler.json#s8`
