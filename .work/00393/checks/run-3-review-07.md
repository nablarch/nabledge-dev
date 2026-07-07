# review-07 — run-3

## 質問

外部サイトから不正にPOSTされるのを防ぎたい。NablarchにCSRF対策の仕組みはある？どう設定する？

## 回答

**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）があります。このハンドラをハンドラ構成に追加するだけで、CSRFトークンの生成と検証が自動的に行われます。

**根拠**:

**基本設定（JSPカスタムタグを使う場合）**

ハンドラ構成に `CsrfTokenVerificationHandler` を追加します。配置順に注意が必要です。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**デフォルトの動作**

- **トークン生成**: セッションストアにCSRFトークンがない場合、UUID v4 (`UUIDv4CsrfTokenGenerator`) で自動生成しセッションストアへ保存
- **検証対象**: `GET`・`HEAD`・`TRACE`・`OPTIONS` は検証対象外。`POST`・`PUT` 等は検証対象
- **トークンの受け取り**: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` から取得
- **検証失敗時**: BadRequest(400) を返す
- JSPカスタムタグを使っている場合は、hidden暗号化の仕組みでCSRFトークンが画面に自動出力されるため、アプリケーションプログラマが実装する必要はありません

**注意点**:

- `CsrfTokenVerificationHandler` は **セッション変数保存ハンドラ（`SessionStoreHandler`）より後ろ**に配置すること
- JSPカスタムタグを使う場合は **`NablarchTagHandler` より後ろ**に配置すること
- ハンドラを使うには **セッションストアが必須**（CSRFトークンをセッションストアに格納するため）
- **ログイン時の注意**: ログイン成功後にセッションストアをそのまま使い続ける場合（セッションID再生成のみ）は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストアを破棄・再生成する実装であれば不要
- **テスト時**: リクエスト単体テストではCSRFトークン検証が失敗するため、テスト用設定で本ハンドラを `NopHandler` に差し替えて無効化すること

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

## 参照ナレッジ

- [CSRFトークンの生成と検証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンの生成と検証) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#制約) (s3)
- [CSRFトークンを再生成する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンを再生成する) (s5)
- [CSRF （クロスサイト・リクエスト・フォージェリ）](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md#csrf-クロスサイトリクエストフォージェリ) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the single key fact in the Expected Output: that adding the CSRF token verification handler (CsrfTokenVerificationHandler) to the handler configuration enables automatic generation and verification of CSRF tokens. The Actual Output not only confirms this core claim but provides extensive additional detail about configuration, default behavior, and caveats. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about preventing unauthorized POST requests from external sites and how to configure CSRF protection in Nablarch. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う」は回答の結論「このハンドラをハンドラ構成に追加するだけで、CSRFトークンの生成と検証が自動的に行われます」に含まれている |
| answer_relevancy | NG | 回答末尾の「参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし（UUID v4生成・検証対象外メソッド・トークン取得箇所・400応答・ハンドラ配置順・ログイン時再生成・テスト時NopHandler差し替えすべてナレッジ記述と一致） |

### 参照事実（expected_facts）

- CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う
