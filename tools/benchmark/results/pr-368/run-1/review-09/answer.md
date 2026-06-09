**結論**: `SecureHandler`（セキュアハンドラ）のコンポーネント設定に `ContentSecurityPolicyHeader` を追加することで、CSPヘッダをレスポンスに付与できる。JSPカスタムタグを使用している場合はnonce方式が推奨される。

---

**根拠**:

#### パターン1: 固定のCSPヘッダを設定する

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` というレスポンスヘッダが書き出される。

---

#### パターン2: nonceを生成してCSPヘッダに設定する（JSPカスタムタグ使用時の推奨方式）

Nablarch の JSPカスタムタグはJavaScriptを出力するため、`unsafe-inline` を避けるためにnonce方式を使う。

1. `generateCspNonce` プロパティを `true` に設定する
2. ポリシーに `$cspNonceSource$` プレースホルダーを含める

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

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` というヘッダが出力される。

nonce生成が有効になると、JSPカスタムタグの動作が次のように変化する。
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性にnonceを自動設定する
- `scriptタグ` が生成するscript要素のnonce属性にnonceを自動設定する
- `cspNonceタグ` でnonce値をJSP内の任意の要素に埋め込めるようになる

---

#### パターン3: report-onlyモードで動作させる

既存アプリへの段階的な適用や検証に使用する。`reportOnly` を `true` に設定する。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが出力される（ポリシー違反はブロックせずレポートのみ）。

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定すること（HTTPレスポンスハンドラがServletのレスポンスオブジェクトにヘッダを設定するため）
- `secureResponseHeaderList` を明示的に設定する場合、デフォルトのヘッダ（`FrameOptionsHeader`、`XssProtectionHeader` など）も必ず含めること（省略するとそれらのヘッダが無効になる）
- nonceはHTML内に埋め込まれるため、JSPが生成するHTMLはリクエストのたびに変化する

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38