**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler` に `ContentSecurityPolicyHeader` を設定します。JavaScriptを出力するカスタムタグを使用している場合は、nonce方式での対応が必要です。

### 方法1: 固定ポリシーのCSPヘッダを設定する

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を設定します。

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

これにより `Content-Security-Policy: default-src 'self'` ヘッダがレスポンスに付与されます。

### 方法2: nonce付きCSPヘッダを設定する（カスタムタグ使用時）

NablarchのJSPカスタムタグ（`n:form`、`n:script` など）はJavaScriptを生成するため、nonceを使う方式が推奨されます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <!-- ... 他のヘッダ ... -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` プレースホルダーがリクエストごとに `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV` のように置換されます。

nonce有効化後のカスタムタグの動作変化:
- `n:form` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `n:script` が生成するscript要素のnonce属性に自動設定される
- `n:cspNonce` タグでnonceを任意の要素に埋め込めるようになる

### 方法3: report-onlyモードで動作させる（段階的導入時）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダとして出力され、ポリシー違反をブロックせずに検出のみ行います。

### 任意の要素にnonceを埋め込む（`n:cspNonce` タグ）

```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

**注意点**:
- NablarchでのCSP対応はnonce方式を前提としており、HTMLはリクエストのたびに異なる内容になります
- `n:script` タグで作成したscript要素はnonce生成が有効な場合に自動でnonce属性が付与されるため、`n:cspNonce` タグとの二重設定は不要です
- CSPをレスポンスヘッダで設定できない場合は、meta要素での設定も可能です。その場合は `n:cspNonce` の `sourceFormat` 属性を `true` にして `nonce-[nonce値]` フォーマットで出力します

参照: `component/handlers/handlers-secure-handler.json#s6`, `component/handlers/handlers-secure-handler.json#s7`, `component/handlers/handlers-secure-handler.json#s8`, `component/handlers/handlers-secure-handler.json#s9`, `component/libraries/libraries-tag.json#s38`, `component/libraries/libraries-tag.json#s39`