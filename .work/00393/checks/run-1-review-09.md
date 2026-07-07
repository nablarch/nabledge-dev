# review-09 — run-1

## 質問

Content Security Policyを有効にしたい。NablarchのWeb画面でCSPを設定するにはどうすればいい？

## 回答

**結論**: CSPはセキュアハンドラ（`SecureHandler`）に `ContentSecurityPolicyHeader` を追加して設定します。JSPカスタムタグを使用している場合は、nonceを生成するnonce方式が推奨パターンです。

---

**根拠**:

### 1. 固定のCSPヘッダを設定する方法

コンポーネント設定ファイルの `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにポリシー文字列を設定します。

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

→ `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに設定されます。

---

### 2. nonceを使用する方法（JSPカスタムタグ使用時の推奨）

Nablarchのカスタムタグは一部でJavaScriptを出力するため、nonce方式が推奨です。

**手順**:
1. `SecureHandler` の `generateCspNonce` を `true` にする
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

`$cspNonceSource$` はリクエストごとに生成されたnonceに置換されます（例: `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`）。

**nonce有効時のJSPカスタムタグの動作変化**:
- `formタグ` が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素にnonce属性が自動設定される
- `cspNonceタグ` で任意の要素（style要素など）にnonceを埋め込めるようになる

**任意の要素へのnonce埋め込み例**:
```jsp
<%-- style要素にcspNonceタグでnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  /* 省略 */
</style>
```

---

### 3. report-only モード（段階的な適用に有効）

`reportOnly` を `true` にすると、ポリシー違反を強制ではなく報告のみする `Content-Security-Policy-Report-Only` ヘッダが出力されます。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

---

**注意点**:
- `SecureHandler` はハンドラキューで **HTTPレスポンスハンドラよりも後ろに配置すること**（セキュアハンドラが設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIに書き込む順序のため）
- `ContentSecurityPolicyHeader` を追加する際は、デフォルトのヘッダ（`FrameOptionsHeader` 等）も必ず一緒に設定すること

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, handlers-secure-handler.json:s3, libraries-tag.json:s38, libraries-tag.json:s39

## 参照ナレッジ

- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#content-security-policycspに対応する) (s6)
- [固定のContent-Security-Policyヘッダを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#固定のcontent-security-policyヘッダを設定する) (s7)
- [nonceを生成してContent-Security-Policyヘッダに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#nonceを生成してcontent-security-policyヘッダに設定する) (s8)
- [report-only モードで動作させる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#report-only-モードで動作させる) (s9)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#制約) (s3)
- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#content-security-policycspに対応する) (s38)
- [セキュアハンドラが生成したnonceを任意の要素に埋め込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#セキュアハンドラが生成したnonceを任意の要素に埋め込む) (s39)
- [カスタムタグが生成する要素に対してJavaScriptで処理を追加する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#カスタムタグが生成する要素に対してjavascriptで処理を追加する) (s40)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Expected Output contains a single key fact: combining SecureHandler, ContentSecurityPolicyHeader, and custom tag CSP support to enable CSP. The Actual Output comprehensively covers all three components — it details SecureHandler configuration with ContentSecurityPolicyHeader, explains the nonce-based approach for JSP custom tags (including form tag, script tag, and cspNonce tag behavior), and shows how these elements work together. All aspects of the expected fact are explicitly addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to configure Content Security Policy (CSP) in Nablarch's web screen without any irrelevant statements. Great job! |
| faithfulness | 0.99 | 0.88 | NG | The score is 0.88 because the actual output correctly states that SecureHandler must be placed after the HTTP response handler, but incorrectly explains the reason for this ordering. The retrieval context specifies that the HTTP response handler writes the response headers set by SecureHandler to the Servlet API response object, meaning SecureHandler sets the headers first and then the HTTP response handler writes them. The actual output reverses this relationship, misstating the directional dependency between SecureHandler and the HTTP response handler. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「セキュアハンドラとContentSecurityPolicyHeaderとカスタムタグのCSP対応を組み合わせてCSPを有効にする」は回答の「CSPはセキュアハンドラ（SecureHandler）にContentSecurityPolicyHeaderを追加して設定します。JSPカスタムタグを使用している場合は、nonceを生成するnonce方式が推奨パターン」および各セクションの詳細説明に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, handlers-secure-handler.json:s3, libraries-tag.json:s38, libraries-tag.json:s39」という内部JSONファイル参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | 回答の「セキュアハンドラが設定したレスポンスヘッダをHTTPレスポンスハンドラがServlet APIに書き込む順序のため」はナレッジの「本ハンドラで設定したレスポンスヘッダを、HTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトに設定するため」と一致しており矛盾なし。DeepEvalの「関係を逆転している」という判定は誤り |

### 参照事実（expected_facts）

- セキュアハンドラとContentSecurityPolicyHeaderとカスタムタグのCSP対応を組み合わせてCSPを有効にする
