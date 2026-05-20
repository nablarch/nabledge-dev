**結論**: NablarchのウェブアプリケーションでCSPを有効にするには、コンポーネント設定ファイルで `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を設定します。

**根拠**:

CSP対応には2つのアプローチがあります。

**アプローチ1: 固定のCSPヘッダを設定する**

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

この場合、`Content-Security-Policy: default-src 'self'` ヘッダが書き出されます。

**アプローチ2: nonceを生成してCSPに対応する（JSPカスタムタグを使用している場合に推奨）**

NablarchのJSPカスタムタグの一部はJavaScriptを出力するため、nonceを使う方式が必要になります。

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

`$cspNonceSource$` プレースホルダーはリクエストごとに生成された nonce 値（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に自動置換されます。

nonceを有効にすると、JSPカスタムタグの動作が以下のように変化します：
- `formタグ` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素のnonce属性が自動設定される
- `cspNonceタグ` で任意の要素にnonceを出力できるようになる

**アプローチ3: report-only モード（段階的導入時）**

ポリシー違反をログに記録するだけで適用しない場合は `reportOnly` を `true` に設定します：

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

**注意点**:
- `SecureHandler` は必ず `HTTPレスポンスハンドラ` よりも後ろに設定すること（`HTTPレスポンスハンドラ` がServlet APIのレスポンスオブジェクトにヘッダを設定するため）
- `secureResponseHeaderList` に追加する際は、デフォルトの5つのヘッダコンポーネント（`FrameOptionsHeader`、`XssProtectionHeader`、`ContentTypeOptionsHeader`、`ReferrerPolicyHeader`、`CacheControlHeader`）も明示的に設定すること（省略するとデフォルトヘッダが出力されなくなる）
- nonceはHTMLに埋め込まれるため、JSPから生成されるHTMLはリクエストごとに変化する

参照: component/handlers/handlers-secure-handler.json:s6, component/handlers/handlers-secure-handler.json:s7, component/handlers/handlers-secure-handler.json:s8, component/handlers/handlers-secure-handler.json:s9, component/libraries/libraries-tag.json:s38