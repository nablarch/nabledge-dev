**結論**: `SecureHandler`に`ContentSecurityPolicyHeader`を追加することでCSPヘッダを送出できる。nonce対応が必要な場合は`generateCspNonce`プロパティを有効にし、JSP側でカスタムタグのCSP機能を利用する。

---

**根拠**:

**パターン1: 固定ポリシーを設定する（nonce不要の場合）**

コンポーネント定義ファイルで`SecureHandler`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシーを設定する。

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

これにより `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに付与される。

---

**パターン2: nonceを生成してポリシーに埋め込む（JSPカスタムタグを使用している場合に推奨）**

`generateCspNonce`を`true`にし、ポリシーにプレースホルダー`$cspNonceSource$`を含める。

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

`$cspNonceSource$`はリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` として出力される。

nonce有効時のJSPカスタムタグの動作変化:
- `<n:form>`が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `<n:script>`タグが生成するscript要素にnonce属性が自動付与される
- `<n:cspNonce />`タグでnonceを任意の要素（style要素など）に埋め込める

---

**パターン3: report-onlyモードで動作させる（導入前の確認用）**

ポリシー違反を即時ブロックせずにレポートのみ行う場合は`reportOnly`を`true`に設定する。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

---

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろに設定すること（本ハンドラが設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIに設定するため）
- `secureResponseHeaderList`を明示的に設定した場合は、デフォルトのヘッダコンポーネント（FrameOptionsHeaderなど）も漏れなく列挙すること
- nonce対応ではHTMLがリクエスト毎に変化するため、コンテンツキャッシュの扱いに注意が必要

参照:
- セキュアハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md
  Content Security Policy(CSP)に対応する
  固定のContent-Security-Policyヘッダを設定する
  nonceを生成してContent-Security-Policyヘッダに設定する
  report-only モードで動作させる
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  Content Security Policy(CSP)に対応する
  セキュアハンドラが生成したnonceを任意の要素に埋め込む