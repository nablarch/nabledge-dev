**結論**: `SecureHandler`のコンポーネント定義に`ContentSecurityPolicyHeader`を追加することでCSPヘッダを設定できる。JSPカスタムタグを使用している場合はnonceを利用した対応が必要で、`generateCspNonce`プロパティを`true`にする。

---

**根拠**:

### パターン1: 固定のContent-Security-Policyヘッダを設定する

`SecureHandler`の`secureResponseHeaderList`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を指定する。

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

この場合、`Content-Security-Policy: default-src 'self'` というレスポンスヘッダが書き出される。

---

### パターン2: nonceを生成してContent-Security-Policyヘッダに設定する（JSPカスタムタグを使う場合）

NablarchのJSPカスタムタグはJavaScriptを出力するため、`unsafe-inline`を避けるにはnonceが必要。`generateCspNonce`を`true`にすると、リクエストごとにnonceが生成され、ポリシー文字列内のプレースホルダー`$cspNonceSource$`に自動で置換される。

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

`$cspNonceSource$`は`nonce-[生成されたnonce]`に置換され、例えば`Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`のようなヘッダになる。

nonce有効時のJSPカスタムタグの動作変化:
- `formタグ`が生成するJavaScriptをscript要素にまとめ、nonce属性に自動設定する
- `scriptタグ`が生成するscript要素のnonce属性にnonceを設定する
- `cspNonceタグ`でnonceを任意の場所に出力できる（`sourceFormat="true"`でプレフィックス`nonce-`付き）

---

### パターン3: report-onlyモードで動作させる

本番適用前の検証には`reportOnly`を`true`に設定する。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only`ヘッダが書き出される。

---

**注意点**:
- nonceを利用する対応では、HTMLがリクエストの都度変化する（nonce値がリクエストごとに異なる）
- nonceはリクエストスコープに格納されるため、同一リクエスト内で一貫した値が使用される

参照: component/handlers/handlers-secure-handler.json:s6, component/handlers/handlers-secure-handler.json:s7, component/handlers/handlers-secure-handler.json:s8, component/handlers/handlers-secure-handler.json:s9, component/libraries/libraries-tag.json:s38, component/libraries/libraries-tag-reference.json:s56