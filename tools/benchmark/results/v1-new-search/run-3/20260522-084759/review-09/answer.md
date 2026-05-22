必要な情報が揃いました。Step 5〜8を実行します。

---

**結論**: NablarchのウェブアプリケーションでCSPを設定するには、`SecureHandler` に `ContentSecurityPolicyHeader` を設定します。nonceを使う場合は `generateCspNonce=true` を指定し、JSPカスタムタグのCSP対応と組み合わせます。

---

**根拠**:

### パターン1: 固定のContent-Security-Policyヘッダを設定する

`ContentSecurityPolicyHeader` を `SecureHandler` の `secureResponseHeaderList` に追加し、`policy` プロパティにポリシー文字列を設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

この設定で `Content-Security-Policy: default-src 'self'` ヘッダが出力されます。

---

### パターン2: nonceを使ってCSPを設定する（推奨）

NablarchのJSPカスタムタグはJavaScriptを出力するため、`unsafe-inline` を使わずに対応するにはnonceを使います。

1. `SecureHandler` の `generateCspNonce` を `true` に設定
2. ポリシーに `$cspNonceSource$` プレースホルダーを含める

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <!-- nonceを生成するように設定する -->
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のように出力されます。

**nonce有効時のJSPカスタムタグの動作変化**:
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性に生成したnonceを設定
- `scriptタグ` が生成するscript要素のnonce属性にnonceを自動設定
- `<n:cspNonce />` タグで任意の要素にnonceを埋め込める

```jsp
<%-- style要素など任意の要素にnonceを設定する場合 --%>
<style nonce="<n:cspNonce />">
  /* ... */
</style>
```

---

### パターン3: report-onlyモード（段階的導入に有効）

本番適用前に違反をログで確認したい場合は `reportOnly=true` を設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合 `Content-Security-Policy-Report-Only` ヘッダが出力されます。

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定すること（SecureHandlerが設定したヘッダをHTTPレスポンスハンドラがServlet APIに反映するため）
- `secureResponseHeaderList` を明示設定する際は、デフォルトのコンポーネント（`FrameOptionsHeader` など）も必ず含めること
- CSPでnonceを使う場合、onclick属性などインラインスクリプトを直接記述すると `unsafe-inline` が必要になりセキュリティレベルが低下するため、外部スクリプトまたはnonce付きscript要素で実装すること

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40

---