NablarchのWeb画面でCSP（Content Security Policy）を設定するには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加して `policy` プロパティにポリシー文字列を設定します。nonce を使う場合は `generateCspNonce` を `true` にして、ポリシーにプレースホルダー `$cspNonceSource$` を含めます。

---

## 設定手順

### (1) 固定のCSPヘッダを設定する場合

コンポーネント設定ファイルの `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティを設定します。

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

これにより `Content-Security-Policy: default-src 'self'` がレスポンスヘッダとして書き出されます。

---

### (2) nonceを使ってインラインスクリプトを許可する場合

`generateCspNonce` を `true` に設定し、ポリシーにプレースホルダー `$cspNonceSource$` を含めます。

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

プレースホルダー `$cspNonceSource$` はリクエストごとに `nonce-[生成されたnonce値]` に置換されます（例: `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`）。JSPで任意の要素にnonceを設定したい場合は `cspNonce` カスタムタグを使用できます。

---

### (3) report-only モードで動作させる（段階的な適用に有効）

`ContentSecurityPolicyHeader` の `reportOnly` を `true` に設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

これにより `Content-Security-Policy-Report-Only` ヘッダが書き出されます。

---

**注意点**:
- `ContentSecurityPolicyHeader` を追加する際は、デフォルトのコンポーネント（`FrameOptionsHeader`、`XssProtectionHeader`、`ContentTypeOptionsHeader`、`ReferrerPolicyHeader`、`CacheControlHeader`）も合わせて設定すること。省略するとそれらのデフォルトヘッダが出力されなくなります。
- `SecureHandler` はウェブアプリケーションの最小ハンドラ構成に含まれており、通常は既に設定済みです。

参照: `handlers-secure-handler.json:s7`, `handlers-secure-handler.json:s8`, `handlers-secure-handler.json:s9`, `handlers-secure-handler.json:s5`, `libraries-tag-reference.json:s56`