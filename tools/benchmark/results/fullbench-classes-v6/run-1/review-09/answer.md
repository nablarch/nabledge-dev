**結論**: CSPはセキュアハンドラ（`SecureHandler`）に `ContentSecurityPolicyHeader` を追加して設定します。JSPカスタムタグを使用している場合は、nonceを生成するnonce方式が推奨パターンです。

---

**根拠**:

### 1. 固定のCSPヘッダを設定する方法

コンポーネント設定ファイルの `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定します。

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

→ `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに設定されます。

---

### 2. nonceを使用する方法（JSPカスタムタグ使用時の推奨）

Nablarchのカスタムタグは一部でJavaScriptを出力するため、nonce方式が推奨です。

**手順**:
1. `SecureHandler` の `generateCspNonce` を `true` にする
2. `policy` にプレースホルダー `$cspNonceSource$` を含める

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

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換されます（例: `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`）。

**nonce有効時のJSPカスタムタグの動作変化**:
- `formタグ` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素にnonce属性が自動設定される
- `cspNonceタグ` で任意の要素（style要素など）にnonceを埋め込めるようになる

**任意の要素へのnonce埋め込み例**:
```jsp
<%-- style要素にcspNonceタグでnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  /* 省略 */
</style>
```

---

### 3. report-only モード（段階的な適用に有効）

`reportOnly` を `true` にすると、ポリシー違反を強制ではなく報告のみする `Content-Security-Policy-Report-Only` ヘッダが出力されます。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

---

**注意点**:
- `SecureHandler` はハンドラキューで **HTTPレスポンスハンドラよりも後ろに配置すること**（セキュアハンドラが設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIに書き込む順序のため）
- `ContentSecurityPolicyHeader` を追加する際は、デフォルトのヘッダ（`FrameOptionsHeader` 等）も必ず一緒に設定すること

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, handlers-secure-handler.json:s3, libraries-tag.json:s38, libraries-tag.json:s39