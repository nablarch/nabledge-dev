**結論**: NablarchのWeb画面でCSPを設定するには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加し、必要に応じてnonceを利用します。

## 方法1: 固定のCSPヘッダを設定する

コンポーネント設定で `SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を指定します。

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

これにより `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに付与されます。

## 方法2: nonceを使ったCSP設定（JSPカスタムタグを使用している場合）

NablarchのJSPカスタムタグはJavaScriptを出力するものがあるため、nonce方式が推奨されます。

1. `SecureHandler` の `generateCspNonce` を `true` に設定
2. ポリシー文字列にプレースホルダー `$cspNonceSource$` を含める

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

`$cspNonceSource$` はリクエストごとに生成されたnonce（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に自動置換されます。

nonceを有効にすると、JSPカスタムタグの動作が次のように変化します:
- `form`タグが生成するJavaScriptをscript要素にまとめ、nonce属性を自動設定
- `script`タグが生成するscript要素にnonce属性を自動設定
- `<n:cspNonce />` タグで任意の要素にnonceを埋め込み可能

## 方法3: report-onlyモード（段階的移行に有効）

既存アプリへの影響を確認しながら導入したい場合は `reportOnly` を `true` にします。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダが付与され、ポリシー違反をブロックせず報告のみ行います。

**注意点**:
- JSPカスタムタグを使用している場合は**nonce方式が必須**です。固定ポリシーのみでは `script-src 'unsafe-inline'` などが必要になりCSPの効果が薄れます
- nonceはリクエストごとに生成されるため、nonceを有効にするとJSPから生成されるHTMLがリクエストのたびに変化します（キャッシュに注意）
- インラインscript/styleを外部ファイルに移行できない場合は `<n:cspNonce />` タグでnonce属性を付与できます
- `Content-Security-Policy` をレスポンスヘッダで設定できない場合は、meta要素での設定も可能です（その場合は `<n:cspNonce sourceFormat="true" />` を使用）

参照: `component/handlers/handlers-secure-handler.json#s6`, `component/handlers/handlers-secure-handler.json#s7`, `component/handlers/handlers-secure-handler.json#s8`, `component/handlers/handlers-secure-handler.json#s9`, `component/libraries/libraries-tag.json#s38`, `component/libraries/libraries-tag.json#s39`