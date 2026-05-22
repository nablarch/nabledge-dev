Step 5-7: 回答を生成し、ベリファイを行います。

---

**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加することでCSPヘッダを設定できます。nonceを使う場合は `generateCspNonce="true"` を設定し、JSPカスタムタグと連携させます。

---

**根拠**:

### パターン1: 固定のContent-Security-Policyヘッダを設定する

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシーを設定します。

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

これにより `Content-Security-Policy: default-src 'self'` というレスポンスヘッダが書き出されます。

---

### パターン2: nonceを生成してCSPヘッダに設定する（JSPカスタムタグを使用する場合）

NablarchのJSPカスタムタグはJavaScriptを出力するものがあるため、nonceを使った対応が推奨されます。

1. `SecureHandler` の `generateCspNonce` を `true` に設定する
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

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` として出力されます。

この設定を行うと、JSPカスタムタグの動作が自動的に変化します：
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素のnonce属性にnonceが自動設定される

#### style要素など任意の要素にnonceを付与したい場合

`<n:cspNonce />` タグを使用します。

```jsp
<%-- cspNonceタグを使用してnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

出力されるHTML:
```html
<style nonce="DhcnhD3khTMePgXwdayK9BsMqXjhguVV">
  <!-- 省略 -->
</style>
```

---

### パターン3: report-onlyモードで動作させる（段階的導入）

`ContentSecurityPolicyHeader` の `reportOnly` を `true` に設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合 `Content-Security-Policy-Report-Only` ヘッダが出力され、ポリシー違反を検知しながら実際のブロックは行いません。

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも **後ろ** に設定すること（本ハンドラが設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIへ設定するため）
- nonceを使う場合、JSPから生成されるHTMLがリクエストの都度変化する（キャッシュ制御に注意）
- カスタムタグが生成する要素にJavaScriptで処理を追加したい場合は、`suppressDefaultSubmit="true"` でカスタムタグのJS生成を抑制し、外部ファイルまたはnonce付きscript要素として実装すること

参照: `handlers-secure-handler.json:s6`, `handlers-secure-handler.json:s7`, `handlers-secure-handler.json:s8`, `handlers-secure-handler.json:s9`, `libraries-tag.json:s38`, `libraries-tag.json:s39`, `libraries-tag.json:s40`, `libraries-tag-reference.json:s56`

---