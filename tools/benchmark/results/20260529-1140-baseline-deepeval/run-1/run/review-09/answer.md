**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を設定します。固定ポリシーで設定するか、nonceを使って動的に設定する2つの方法があります。

**根拠**:

#### 方法1: 固定のContent-Security-Policyヘッダを設定する

`ContentSecurityPolicyHeader`を`SecureHandler`に追加し、`policy`プロパティにポリシー文字列を設定します。

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

この設定により `Content-Security-Policy: default-src 'self'` というレスポンスヘッダが付与されます。

#### 方法2: nonceを生成してContent-Security-Policyヘッダに設定する（推奨）

NablarchのカスタムタグはJavaScriptを出力するため、`unsafe-inline`を避けてnonceを使う方式が適しています。`generateCspNonce`を`true`にすると、カスタムタグが自動的にnonce属性を設定します。

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

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` というプレースホルダーがリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のようなヘッダが出力されます。

nonceモード有効時のカスタムタグの動作変化:
- `formタグ`が生成するJavaScriptをscript要素にまとめ、nonce属性にnonceを設定する
- `scriptタグ`が生成するscript要素のnonce属性にnonceを設定する
- `cspNonceタグ`でnonceを任意の要素に出力できる

#### report-onlyモード（段階的導入時）

`reportOnly`を`true`にすると`Content-Security-Policy-Report-Only`ヘッダを使ったレポート専用モードで動作させられます。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

**注意点**: NablarchのCSP対応はnonceを利用して実現します。nonceはHTMLに埋め込まれるため、JSPから生成されるHTMLがリクエストの都度変化します。

参照:
- handlers-secure-handler.json:s6
- handlers-secure-handler.json:s7
- handlers-secure-handler.json:s8
- handlers-secure-handler.json:s9
- libraries-tag.json:s38
- libraries-tag-reference.json:s56

---