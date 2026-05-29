セクション内容が揃いました。回答を生成します。

---

**結論**: NablarchのウェブアプリケーションでCSPを有効にするには、`SecureHandler` に `ContentSecurityPolicyHeader` を設定し、カスタムタグのnonce機能と組み合わせて対応します。

**根拠**:

**1. 固定ポリシーで設定する場合（nonce不要）**

コンポーネント設定ファイルに `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシーを設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

これで `Content-Security-Policy: default-src 'self'` レスポンスヘッダが出力されます。

**2. nonce を使用してインラインスクリプトを許可する場合**

Nablarchのカスタムタグ（`n:form`、`n:submit` など）はJavaScriptをインラインで出力するため、CSP対応にはnonceが必要です。`generateCspNonce` を `true` に設定し、ポリシーに `$cspNonceSource$` プレースホルダーを含めます。

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

`$cspNonceSource$` は `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV` のように実際のnonce値に置換されます。nonceはリクエストごとに生成され、カスタムタグが生成する `script` 要素に自動でnonce属性が付与されます。

**3. report-only モードで先行検証する場合**

`reportOnly` を `true` にすると `Content-Security-Policy-Report-Only` ヘッダが出力され、実際に制御せずに違反を検知・収集できます。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

**4. 任意の要素にnonceを埋め込む場合（JSP）**

`n:cspNonce` タグを使用すると、`style` 要素などにもnonceを付与できます。

```jsp
<style nonce="<n:cspNonce />">
  /* スタイル */
</style>
```

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定してください（レスポンスハンドラがServletAPIのレスポンスにヘッダを書き込む仕組みのため）。
- CSP対応時、インラインJavaScript（onclick属性など）は `unsafe-inline` なしには動作しなくなります。カスタムタグの `onclick` 属性でインラインスクリプトを記述している場合、外部ファイルまたはnonce付き `script` 要素に移行してください。

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39

---