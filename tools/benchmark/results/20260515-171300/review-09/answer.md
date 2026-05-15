**結論**: NablarchのWeb画面でCSPを設定するには、`SecureHandler`に`ContentSecurityPolicyHeader`を追加します。nonce対応が必要な場合は`generateCspNonce`プロパティも有効にします。

**根拠**:

**パターン1: 固定のContent-Security-Policyヘッダを設定する**

`SecureHandler`のコンポーネント設定に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を指定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- CSPヘッダを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

結果: `Content-Security-Policy: default-src 'self'` がレスポンスに付与されます。

---

**パターン2: nonceを生成してCSPヘッダに設定する（JSPカスタムタグを使用している場合）**

JSPカスタムタグはJavaScriptを出力するため、nonce方式で対応します。

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

`generateCspNonce`を`true`にすると、以下の変化が起きます:
- `$cspNonceSource$`プレースホルダーが`nonce-[生成値]`に置換されてヘッダに出力される
- JSPの`<n:script>`タグが生成するscript要素にnonce属性が自動付与される
- `<n:form>`タグが生成するJavaScriptがscript要素にまとめられnonce属性が設定される

---

**パターン3: report-onlyモード（段階的導入に有効）**

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

結果: `Content-Security-Policy-Report-Only` ヘッダとして出力されます（ブロックせずに違反を報告のみ）。

---

**インラインスクリプトへのnonce埋め込み（JSPカスタムタグ以外の要素）**

既存のインラインスクリプト/スタイルにnonceを付与する場合は`<n:cspNonce />`タグを使用します:

```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも**後ろ**に設定する必要があります（HTTPレスポンスハンドラがServlet APIのレスポンスに実際にヘッダを書き出すため）
- `secureResponseHeaderList`を明示的に設定する場合は、デフォルトの5つのヘッダコンポーネント（`FrameOptionsHeader`、`XssProtectionHeader`、`ContentTypeOptionsHeader`、`ReferrerPolicyHeader`、`CacheControlHeader`）も必ず含めること（指定しないと適用されなくなる）
- nonceを使用する場合、JSPから生成されるHTMLがリクエストのたびに変化するため、HTTPキャッシュの扱いに注意が必要です
- nonce方式を採用しても、インラインスクリプトはできる限り外部ファイルに移行することが推奨されます

参照: `component/handlers/handlers-secure-handler.json#s6`, `component/handlers/handlers-secure-handler.json#s7`, `component/handlers/handlers-secure-handler.json#s8`, `component/handlers/handlers-secure-handler.json#s9`, `component/libraries/libraries-tag.json#s38`, `component/libraries/libraries-tag.json#s39`