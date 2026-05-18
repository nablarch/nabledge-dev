**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler` に `ContentSecurityPolicyHeader` を設定します。nonce を使う場合は `generateCspNonce` を `true` にした上で、JSPカスタムタグと組み合わせます。

**根拠**:

### 基本設定（固定ポリシー）

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

これにより `Content-Security-Policy: default-src 'self'` レスポンスヘッダが付与されます。

### nonce を使う場合

NablarchのJSPカスタムタグ（`<n:form>` など）はJavaScriptを出力するため、nonceを使ったCSP対応が推奨されます。

1. `SecureHandler` の `generateCspNonce` を `true` に設定
2. `policy` にプレースホルダー `$cspNonceSource$` を含める

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

`$cspNonceSource$` はリクエストごとに生成されたnonce値に自動置換されます。

nonce 有効時のカスタムタグの動作変化:
- `<n:form>` が生成するJavaScriptはscript要素にまとめられ、nonce属性が自動設定される
- `<n:script>` が生成するscript要素のnonce属性にnonceが自動設定される
- `<n:cspNonce />` タグでnonceを任意の要素に埋め込めるようになる

任意の要素にnonceを付与したい場合:
```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

### report-only モードで試験運用する場合

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

**注意点**:
- NablarchのCSP対応はnonceを前提としています。nonceはHTMLに埋め込まれるため、JSPから生成されるHTMLはリクエストのたびに変化します（キャッシュ戦略に影響する場合があります）
- インラインスクリプト・スタイルは原則として外部ファイルへ移行することが推奨されます。移行困難な場合のみ `<n:cspNonce />` タグで対応してください
- `Content-Security-Policy` をレスポンスヘッダで設定できない事情がある場合は `meta` 要素で設定する代替手段もあります。その場合は `<n:cspNonce sourceFormat="true" />` を使用してください

参照: `component/handlers/handlers-secure-handler.json#s6`, `component/handlers/handlers-secure-handler.json#s7`, `component/handlers/handlers-secure-handler.json#s8`, `component/handlers/handlers-secure-handler.json#s9`, `component/libraries/libraries-tag.json#s38`, `component/libraries/libraries-tag.json#s39`