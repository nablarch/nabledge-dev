# review-07 — run-2

## 質問

外部サイトから不正にPOSTされるのを防ぎたい。NablarchにCSRF対策の仕組みはある？どう設定する？

## 回答

**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラ構成に追加するだけでCSRF対策を漏れなく適用できます。

**根拠**:

`CsrfTokenVerificationHandler` をハンドラキューに追加することで、POSTなどのリクエストに対してCSRFトークンの検証が自動実行されます。以下の設定が最小構成です。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（先に配置） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時、先に配置） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**デフォルトの動作**:
- セッションストアにCSRFトークンを保存（名前: `nablarch_csrf-token`）
- トークン生成: バージョン4のUUID（`UUIDv4CsrfTokenGenerator`）
- 検証対象外: `GET` `HEAD` `TRACE` `OPTIONS`（POSTやPUT等は検証対象）
- CSRFトークンのリクエスト送信方法: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: BadRequest(400)レスポンスを返却

**JSPカスタムタグ使用時**: `NablarchTagHandler` が画面にCSRFトークンを自動出力するため、アプリ実装なしでトークンが埋め込まれます。

**注意点**:
- `CsrfTokenVerificationHandler` は必ずセッション変数保存ハンドラ（`SessionStoreHandler`）より後ろに配置すること。セッションストアの使用が必須です。
- JSP利用時は `NablarchTagHandler` より後ろに配置すること。
- データベースを使用した二重サブミット防止機能（`DbTokenManager`）はCSRF対策に対応していないため、CSRF対策には本ハンドラを使用すること。
- ログイン時にセッションIDのみ再生成する場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成する必要があります。
- リクエスト単体テストではCSRFトークン検証が失敗するため、テスト設定で `NopHandler` に差し替えて無効化してください。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

## 参照ナレッジ

- [CSRFトークンの生成と検証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンの生成と検証) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#制約) (s3)
- [CSRFトークンを再生成する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンを再生成する) (s5)
- [CSRF （クロスサイト・リクエスト・フォージェリ）](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md#csrf-クロスサイトリクエストフォージェリ) (s6)
- [CSRF対策](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#csrf対策) (s19)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the single fact in the Expected Output: that adding the CSRF token verification handler (CsrfTokenVerificationHandler) to the handler configuration enables CSRF token generation and verification. The Actual Output explicitly states this and provides extensive additional detail about configuration, default behavior, and caveats, all of which reinforce the core fact. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about preventing unauthorized POST requests from external sites and explaining Nablarch's CSRF protection mechanism and its configuration. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う」は回答の「`CsrfTokenVerificationHandler` をハンドラキューに追加することで、POSTなどのリクエストに対してCSRFトークンの検証が自動実行されます」に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う
