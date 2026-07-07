# review-09 — run-3

## 質問

Content Security Policyを有効にしたい。NablarchのWeb画面でCSPを設定するにはどうすればいい？

## 回答

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

## 参照ナレッジ

- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#content-security-policycspに対応する) (s6)
- [固定のContent-Security-Policyヘッダを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#固定のcontent-security-policyヘッダを設定する) (s7)
- [nonceを生成してContent-Security-Policyヘッダに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#nonceを生成してcontent-security-policyヘッダに設定する) (s8)
- [report-only モードで動作させる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#report-only-モードで動作させる) (s9)
- [Content Security Policy(CSP)対応](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#content-security-policycsp対応) (s21)
- [cspNonceタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#cspnonceタグ) (s56)
- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#content-security-policycspに対応する) (s38)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.90 | NG | The Expected Output is a brief high-level statement about combining SecureHandler, ContentSecurityPolicyHeader, and custom tags to enable CSP. The Actual Output comprehensively covers all three elements: SecureHandler configuration with ContentSecurityPolicyHeader, nonce generation for JSP custom tags, and additional patterns like report-only mode. The Actual Output fully addresses the core facts in the Expected Output — SecureHandler integration, ContentSecurityPolicyHeader usage, and custom tag CSP support with nonce — providing detailed examples that align with and exceed the expected coverage. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to configure Content Security Policy (CSP) in Nablarch's web screen without any irrelevant statements. Great job! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- セキュアハンドラとContentSecurityPolicyHeaderとカスタムタグのCSP対応を組み合わせてCSPを有効にする
