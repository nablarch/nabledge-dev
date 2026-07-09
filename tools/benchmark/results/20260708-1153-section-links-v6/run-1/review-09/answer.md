**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、CSPポリシーを設定する。JSPカスタムタグを使用している場合は `generateCspNonce` を `true` にしてnonceを生成・埋め込む方式が推奨される。

---

**根拠**:

**方法1: 固定のContent-Security-Policyヘッダを設定する**

コンポーネント定義ファイルに `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` というレスポンスヘッダが出力される。

**方法2: nonceを生成してCSPヘッダに設定する（JSPカスタムタグを使用している場合）**

Nablarchのカスタムタグはサブミット時にJavaScriptを生成するため、nonceを使った対応が必要になる。`generateCspNonce` を `true` にし、ポリシーにプレースホルダー `$cspNonceSource$` を含める。

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

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換される（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）。

nonce生成を有効にすると、カスタムタグの動作が次のように変化する：
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性を自動設定する
- `scriptタグ` が生成するscript要素のnonce属性を自動設定する
- `<n:cspNonce />` タグで任意の要素にnonceを出力できる（styleタグ等へのnonce付与に使用）

```jsp
<%-- style要素にnonceを付与する例 --%>
<style nonce="<n:cspNonce />">
  /* ... */
</style>
```

**方法3: report-onlyモードで段階的に導入する**

既存のアプリケーションに段階的に導入する場合、`reportOnly` を `true` にすることで `Content-Security-Policy-Report-Only` ヘッダで試験運用できる。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定する必要がある
- Nablarchのカスタムタグを使用している場合は固定ポリシーのみでは対応できないため、nonceを使う方式が推奨される
- onclick属性などにインラインスクリプトを書くと、CSPポリシーを緩めることになるため注意。カスタムタグの `suppressDefaultSubmit="true"` 属性と外部スクリプトの組み合わせで対応する

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
  カスタムタグが生成する要素に対してJavaScriptで処理を追加する