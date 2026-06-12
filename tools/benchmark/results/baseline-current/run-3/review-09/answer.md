**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加設定します。nonce を使う場合は `generateCspNonce` を `true` にし、JSPカスタムタグと組み合わせます。

**根拠**:

### 1. 固定のCSPヘッダを設定する（最もシンプルな方法）

`SecureHandler` のコンポーネント設定ファイルに `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- CSPヘッダを追加 -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

結果: `Content-Security-Policy: default-src 'self'` がレスポンスに付与されます。

### 2. nonce を使って CSP を設定する（JSPカスタムタグを使用している場合）

Nablarch の JSP カスタムタグは JavaScript を出力するため、nonce による対応が推奨されます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <!-- nonceを生成する -->
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- $cspNonceSource$ がnonceに置換される -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエスト毎に生成された nonce（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に自動置換されます。

nonce 有効時の JSP カスタムタグの動作変化:
- `formタグ` が生成する JavaScript が `script` 要素にまとめられ、nonce 属性が自動付与される
- `scriptタグ` が生成する `script` 要素にも nonce 属性が自動付与される

### 3. 任意の要素に nonce を埋め込む（`cspNonce` タグ）

インラインスタイルなど、外部ファイル化が難しい要素には `<n:cspNonce />` タグを使います。

```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

### 4. report-only モード（段階的に導入する場合）

既存アプリに対して CSP を試験導入する際は、`reportOnly` を `true` にすると違反をレポートするのみでブロックしません。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

**注意点**:
- `SecureHandler` は **HTTPレスポンスハンドラより後ろに**設定する必要があります（HTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトにヘッダを書き出すため）
- `secureResponseHeaderList` を明示する際は、デフォルトの5つのヘッダ（`FrameOptionsHeader` 等）も必ず一緒に設定してください。省略するとそれらのヘッダが無効になります
- nonce を使う場合、HTML がリクエスト毎に変化するため、CDNやキャッシュ戦略に影響が出ます

参照: `component/handlers/handlers-secure-handler.json#s6`, `#s7`, `#s8`, `#s9`, `component/libraries/libraries-tag.json#s38`, `#s39`