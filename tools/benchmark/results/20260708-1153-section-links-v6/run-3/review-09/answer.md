**結論**: `SecureHandler` のコンポーネント定義に `ContentSecurityPolicyHeader` を追加することで CSP ヘッダを設定できる。nonce を使う場合は `generateCspNonce` プロパティを `true` にすることで、カスタムタグが自動でnonce対応する。

**根拠**:

**パターン1: 固定の CSP ヘッダを設定する**

コンポーネント定義ファイルで `SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定する。

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

これにより `Content-Security-Policy: default-src 'self'` ヘッダが書き出される。

---

**パターン2: nonce を使う（Nablarch カスタムタグを使用している場合に推奨）**

Nablarch のカスタムタグは一部で JavaScript を出力するため、nonce による対応が必要。

1. `generateCspNonce` を `true` に設定する
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

`$cspNonceSource$` は `nonce-[生成されたnonce]` に置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のようなヘッダになる。

nonce 生成が有効な場合、カスタムタグの動作が自動的に変化する：
- `formタグ` が生成する JavaScript が script 要素にまとめられ、nonce 属性が自動設定される
- `scriptタグ` が生成する script 要素にも nonce 属性が自動設定される
- `cspNonceタグ` でnonce値を任意の要素に埋め込める

JSP での `cspNonceタグ` の使用例（style 要素への nonce 付与）：

```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

---

**パターン3: report-only モード（段階的移行時に有用）**

`reportOnly` を `true` に設定することで違反を検知のみ（適用しない）にできる。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合 `Content-Security-Policy-Report-Only` ヘッダが書き出される。

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` より後ろのハンドラキューに設定すること（本ハンドラが設定したレスポンスヘッダを `HTTPレスポンスハンドラ` が Servlet API のレスポンスオブジェクトに設定するため）
- nonce を使う場合、JSP から生成される HTML がリクエストごとに変化する（nonce がリクエスト都度生成されるため）
- カスタムタグが生成する要素に JavaScript で処理を追加する場合は、onclick 属性でインラインスクリプトを直接指定せず、`suppressDefaultSubmit="true"` と外部ファイルまたは nonce 付き script 要素を組み合わせること

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