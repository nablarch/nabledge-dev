**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を設定し、nonceを使用する場合は`generateCspNonce`プロパティを`true`に設定します。

**根拠**:

**パターン1: 固定のCSPヘッダを設定する場合**

`SecureHandler`のコンポーネント定義に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシーを設定します。

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

**パターン2: nonceを使用する場合（JSPカスタムタグを使用している場合に推奨）**

NablarchのJSPカスタムタグはJavaScriptを生成するため、nonceを使った対応が必要です。

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
        <!-- $cspNonceSource$ プレースホルダーが実際のnonceに置換される -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$`は`nonce-[生成されたnonce]`に置換され、例えば`Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`のように出力されます。

`generateCspNonce`を有効にすると、JSPカスタムタグの動作も次のように変化します：
- `formタグ`が生成するJavaScriptはscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ`が生成するscript要素にnonce属性が自動設定される
- `<n:cspNonce />`タグを使って任意の要素にnonceを埋め込める

**パターン3: report-onlyモードで動作させる場合**

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only`ヘッダとして出力されます。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろに設定すること（本ハンドラで設定したヘッダをHTTPレスポンスハンドラがServlet APIに設定するため）
- `secureResponseHeaderList`を設定する際は、デフォルトのコンポーネント（`FrameOptionsHeader`等）も明示的に設定すること

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38