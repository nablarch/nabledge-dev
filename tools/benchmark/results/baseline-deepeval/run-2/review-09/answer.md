Step 5〜7: 回答を生成し、verify します。

**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加することでCSPヘッダを有効化できます。nonceを使う場合は `generateCspNonce=true` も設定し、JSPカスタムタグのCSP対応を組み合わせて利用します。

---

**根拠**:

**パターン1: 固定CSPヘッダを設定する**

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` を設定します。

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

これにより `Content-Security-Policy: default-src 'self'` ヘッダが付与されます。

---

**パターン2: nonceを使ってCSPを設定する（Nablarchカスタムタグを使っている場合）**

Nablarchのカスタムタグ（formタグ、submitタグなど）はJavaScriptを生成するため、nonce方式を使います。

1. `generateCspNonce=true` でnonceを生成
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

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` として出力されます。

**nonce有効時のカスタムタグの変化:**
- `formタグ` が生成するJavaScriptはscript要素にまとめられ、nonce属性が自動付与される
- `scriptタグ` (`<n:script>`) が生成するscript要素のnonce属性も自動で設定される
- `cspNonceタグ` (`<n:cspNonce />`) で任意の要素にnonceを埋め込めるようになる

**style要素へのnonce設定例（JSP）:**

```jsp
<%-- cspNonceタグ使用してnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

出力されるHTML:
```html
<!-- セキュアハンドラが生成したnonceが出力される -->
<style nonce="DhcnhD3khTMePgXwdayK9BsMqXjhguVV">
  <!-- 省略 -->
</style>
```

---

**report-onlyモードで段階的に導入する場合:**

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダが出力され、違反をブロックせずレポートのみ行います。

---

**注意点**:
- `SecureHandler` はハンドラキューにおいて **`HTTPレスポンスハンドラ` より後ろ** に設定する必要があります（SecureHandlerが設定したレスポンスヘッダをHTTPレスポンスハンドラがServletのレスポンスオブジェクトに設定するため）。
- カスタムタグが生成する要素にJavaScriptで処理を追加したい場合、`onclick` 属性でインラインスクリプトを直接指定するとポリシーを緩める必要が生じます。代わりに `suppressDefaultSubmit="true"` でカスタムタグのJavaScript生成を抑制し、外部ファイルまたはnonce付きscript要素でイベント登録する方法を使ってください。
- nonceを使う場合、HTMLはリクエスト毎に異なるnonce値が埋め込まれるため、レスポンスのキャッシュに注意が必要です。

参照: `handlers-secure-handler.json:s6`, `handlers-secure-handler.json:s7`, `handlers-secure-handler.json:s8`, `handlers-secure-handler.json:s9`, `libraries-tag.json:s38`, `libraries-tag.json:s39`, `libraries-tag.json:s40`, `libraries-tag-reference.json:s56`, `handlers-secure-handler.json:s3`

---