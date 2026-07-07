# review-09 — run-2

## 質問

Content Security Policyを有効にしたい。NablarchのWeb画面でCSPを設定するにはどうすればいい？

## 回答

**結論**: NablarchのウェブアプリケーションでCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を設定してレスポンスヘッダを出力し、nonceを使う場合は`generateCspNonce`プロパティを`true`にした上でJSPに`<n:cspNonce />`タグを組み合わせる。

**根拠**:

#### 方法1: 固定のContent-Security-Policyヘッダを設定する

コンポーネント設定ファイルの`SecureHandler`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` のようなレスポンスヘッダが出力される。

#### 方法2: nonceを生成してCSPに対応する（JSPカスタムタグと組み合わせる場合）

NablarchのJSPカスタムタグはJavaScriptを生成するため、nonceを使って対応する。

**ハンドラの設定:**

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

プレースホルダー `$cspNonceSource$` はリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のようなヘッダが出力される。

この設定を行うと、`<n:formタグ>`や`<n:scriptタグ>`が生成するscript要素に自動でnonce属性が設定される。

任意の要素（例: style要素）にnonceを設定したい場合は`<n:cspNonce />`タグを使用する:

```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

#### 方法3: report-onlyモード（動作確認用）

本番適用前の確認として、ポリシー違反を報告するだけで制限しないモードも利用できる:

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが出力される。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろ（内側）に設定すること（`HTTPレスポンスハンドラ`がServletのレスポンスオブジェクトにヘッダを設定するため）。
- nonceを使う場合、生成されるHTMLはリクエスト毎に変化する。
- `secureResponseHeaderList`を設定する際は、デフォルトで適用されていた他のヘッダコンポーネント（`FrameOptionsHeader`等）も一緒に列挙すること。

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39

## 参照ナレッジ

- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#content-security-policycspに対応する) (s6)
- [固定のContent-Security-Policyヘッダを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#固定のcontent-security-policyヘッダを設定する) (s7)
- [nonceを生成してContent-Security-Policyヘッダに設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#nonceを生成してcontent-security-policyヘッダに設定する) (s8)
- [report-only モードで動作させる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#report-only-モードで動作させる) (s9)
- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#content-security-policycspに対応する) (s38)
- [セキュアハンドラが生成したnonceを任意の要素に埋め込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#セキュアハンドラが生成したnonceを任意の要素に埋め込む) (s39)
- [カスタムタグが生成する要素に対してJavaScriptで処理を追加する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#カスタムタグが生成する要素に対してjavascriptで処理を追加する) (s40)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Expected Output contains a single high-level fact: CSP is enabled by combining SecureHandler with ContentSecurityPolicyHeader and custom tags. The Actual Output covers all three components mentioned — SecureHandler, ContentSecurityPolicyHeader, and JSP custom tags (n:cspNonce) — and explains how they work together. The expected fact is fully represented and not contradicted. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the input, directly addressing how to configure Content Security Policy (CSP) in Nablarch's web screen without any irrelevant statements. Great job! |
| faithfulness | 0.99 | 0.93 | NG | The score is 0.93 because the actual output incorrectly attributes the `reportOnly` property to `ContentSecurityPolicyHeader` rather than `SecureHandler`, and misidentifies where the logic for writing the `Content-Security-Policy-Report-Only` header is controlled. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- セキュアハンドラとContentSecurityPolicyHeaderとカスタムタグのCSP対応を組み合わせてCSPを有効にする
