**結論**: NablarchのWeb画面でCSPを設定するには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加し、ポリシー文字列を設定します。JSPカスタムタグを使用している場合はnonceを併用する必要があります。

**根拠**:

### 方法1: 固定のCSPヘッダを設定する

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

これにより `Content-Security-Policy: default-src 'self'` ヘッダが出力されます。

### 方法2: nonceを生成してCSPヘッダに設定する（JSPカスタムタグを使用する場合）

NablarchのJSPカスタムタグはJavaScriptを出力するため、nonceを使用してCSPに対応する必要があります。

1. `SecureHandler` の `generateCspNonce` を `true` に設定する
2. `ContentSecurityPolicyHeader` の `policy` にプレースホルダー `$cspNonceSource$` を含める

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエスト毎に生成されたnonceに自動置換されます（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）。

nonceを有効にすると、JSPカスタムタグの動作が次のように変化します：
- `formタグ` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素のnonce属性にnonceが自動設定される
- `cspNonceタグ` でnonce値を任意の要素に出力できるようになる

### 方法3: report-onlyモード（段階的導入）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダが出力され、違反はレポートされますがコンテンツはブロックされません。

**注意点**:
- `SecureHandler` は **HTTPレスポンスハンドラよりも後ろ**に設定すること。SecureHandlerで設定したヘッダをHTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトに設定するため、順序が重要です。
- nonceを使用する場合、HTMLがリクエストの都度変化します（nonce値が毎回異なるため）。
- 必要なモジュール: `com.nablarch.framework:nablarch-fw-web`

参照: `handlers-secure-handler.json#s6`, `handlers-secure-handler.json#s7`, `handlers-secure-handler.json#s8`, `handlers-secure-handler.json#s9`, `handlers-secure-handler.json#s3`, `libraries-tag.json#s38`