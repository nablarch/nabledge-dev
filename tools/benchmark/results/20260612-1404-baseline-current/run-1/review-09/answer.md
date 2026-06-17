**結論**: `SecureHandler` のコンポーネント設定に `ContentSecurityPolicyHeader` を追加することでCSPを有効にできる。nonceを使うポリシー（`nonce-...`）が必要な場合は `generateCspNonce` を `true` に設定し、ポリシー文字列に `$cspNonceSource$` プレースホルダーを含める。

**根拠**:

**パターン1: 固定のCSPヘッダを設定する**

コンポーネント設定ファイルで `ContentSecurityPolicyHeader` を `SecureHandler` の `secureResponseHeaderList` に追加し、`policy` プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` ヘッダが出力される。

---

**パターン2: nonceを生成してCSPヘッダに設定する（推奨）**

Nablarchのカスタムタグ（formタグ、scriptタグなど）はJavaScriptを出力するため、nonceを使ったポリシーに対応する場合は以下の設定が必要。

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

プレースホルダー `$cspNonceSource$` はリクエストごとに生成された `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV` のような値に置換される。`generateCspNonce=true` を設定すると、formタグ・scriptタグが生成するscript要素のnonce属性にnonceが自動で付与される。

---

**JSPでインライン要素にnonceを埋め込む（`cspNonceタグ`）**

インラインのstyle要素など、任意の要素にnonceを設定したい場合は `cspNonceタグ` を使用する。

```jsp
<%-- cspNonceタグを使用してnonce属性を設定する --%>
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

**パターン3: report-only モードで動作させる**

本番適用前に違反をモニタリングするだけにしたい場合は `reportOnly` を `true` に設定する。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが出力される。

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定すること（本ハンドラで設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIに設定するため）
- nonceはHTML内に埋め込まれるため、JSPから生成されるHTMLはリクエストのたびに変化する
- CSP対応ではインラインスクリプト/スタイルを外部ファイルに移行することが推奨される。すぐに移行できない場合は `cspNonceタグ` で対応する
- `ContentSecurityPolicyHeader` を `secureResponseHeaderList` に追加する際は、デフォルトで適用されていた他のヘッダコンポーネントも一緒に設定すること（省略するとデフォルトヘッダが出力されなくなる）

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, handlers-secure-handler.json:s3, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag-reference.json:s56