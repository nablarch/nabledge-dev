Step 5〜7 で回答を生成し、verify結果はPASSです。

---

**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を設定することでCSPを有効にできます。JSPカスタムタグを使用している場合は nonce を利用した方式が推奨されます。

---

**根拠**:

### 方法1: 固定ポリシーを設定する（シンプルな場合）

コンポーネント設定ファイルで `ContentSecurityPolicyHeader` を `SecureHandler` の `secureResponseHeaderList` に追加します。

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

これにより `Content-Security-Policy: default-src 'self'` というレスポンスヘッダが書き出されます。

---

### 方法2: nonce を使ってCSPを設定する（JSPカスタムタグ利用時の推奨）

NablarchのJSPカスタムタグは一部でJavaScriptを出力するため、nonce方式が推奨されます。

1. `SecureHandler` の `generateCspNonce` プロパティを `true` に設定する
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
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエストごとに生成された nonce 値（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に置換されます。

**nonce 有効化時のカスタムタグの動作変化：**
- `formタグ` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素のnonce属性に nonce が自動設定される
- JSP内で `<n:cspNonce />` タグで nonce を任意の要素に埋め込めるようになる

任意の要素（例：style要素）に nonce を埋め込む場合：

```jsp
<style nonce="<n:cspNonce />">
  /* ... */
</style>
```

---

### 方法3: report-only モードで動作させる（段階的導入時）

先に違反をレポートのみで確認したい場合は `reportOnly` を `true` に設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが書き出されます。

---

**注意点**:

- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに配置すること
- JSPのonclick属性などにインラインスクリプトを記述すると `unsafe-inline` が必要になりCSPの効果が下がる。カスタムタグが生成する要素に処理を追加したい場合は、`suppressDefaultSubmit="true"` を設定してカスタムタグのデフォルトJavaScript生成を抑制し、外部スクリプトまたはnonce付きscript要素でイベントリスナーを追加する方法を使うこと
- nonce を使う場合、JSPから生成されるHTMLはリクエストのたびに変化する（nonceがHTML内に埋め込まれるため）

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40

---