**結論**: NablarchのウェブアプリケーションでCSPを設定するには、`SecureHandler`の`secureResponseHeaderList`に`ContentSecurityPolicyHeader`を追加します。JSPカスタムタグを使用している場合は、`generateCspNonce`を有効にしてnonceベースの対応を行うことが推奨されます。

---

**根拠**:

**1. 固定のContent-Security-Policyヘッダを設定する場合**

コンポーネント設定ファイルで`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシーを設定します。

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
        <!-- ポリシーを設定する -->
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

この場合、`Content-Security-Policy: default-src 'self'` といったレスポンスヘッダが書き出されます。

---

**2. nonceを生成してCSPを設定する場合（JSPカスタムタグ使用時）**

Nablarchのカスタムタグ（`formタグ`など）はJavaScriptを出力するため、nonceベースの対応が必要です。以下のように設定します。

1. `generateCspNonce`プロパティを`true`に設定する
2. `policy`にプレースホルダー`$cspNonceSource$`を含める

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

`$cspNonceSource$`はリクエスト毎に生成されたnonceに置換され、例えば`Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`というヘッダが出力されます。

nonceを有効にすると、カスタムタグの動作が以下のように変化します：
- `scriptタグ`が生成するscript要素のnonce属性にnonceが自動設定される
- `formタグ`が生成するJavaScriptはscript要素にまとめられ、nonce属性が設定される

任意の要素（例：インラインのstyle要素）にnonceを設定したい場合は、`cspNonceタグ`を使用できます：

```jsp
<%-- cspNonceタグ使用してnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

---

**3. report-onlyモードで動作させる場合（段階的導入時）**

`ContentSecurityPolicyHeader`の`reportOnly`を`true`に設定することで、ポリシー違反をブロックせずレポートのみ行うモードで動作できます。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only`ヘッダとして出力されます。

---

**注意点**:
- `SecureHandler`はHTTPレスポンスハンドラよりも後ろに設定すること（本ハンドラで設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトに設定するため）
- `ContentSecurityPolicyHeader`を`secureResponseHeaderList`に追加する際は、デフォルトのヘッダ（`FrameOptionsHeader`など）も明示的に設定すること
- カスタムタグが生成する要素に対してJavaScriptで処理を追加したい場合、インラインスクリプトを直接指定するとポリシーを緩める必要が生じるため、`suppressDefaultSubmit="true"`を設定してカスタムタグによるJavaScript生成を抑制し、外部ファイルまたはnonce付きscript要素で処理を実装すること

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, handlers-secure-handler.json:s3, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40

---