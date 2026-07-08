# review-07 — run-1

## 質問

外部サイトから不正にPOSTされるのを防ぎたい。NablarchにCSRF対策の仕組みはある？どう設定する？

## 回答

**結論**: NablarchのCSRF対策は `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラ構成に追加するだけで有効になる。アプリケーションプログラマが個別に実装する必要はなく、漏れなくチェックできる。

**根拠**:

#### 基本的な設定方法

コンポーネント設定ファイル（XML）のハンドラキューに以下の順序でハンドラを追加する。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（必須：CSRFハンドラより前に配置） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時：CSRFハンドラより前に配置） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

#### デフォルトの動作

| 項目 | デフォルト値 |
|------|-------------|
| トークン生成方式 | UUIDv4（`UUIDv4CsrfTokenGenerator`） |
| 検証対象外のHTTPメソッド | `GET` `HEAD` `TRACE` `OPTIONS` |
| 検証対象 | POST・PUT等（上記以外のメソッド） |
| トークンの送信方法 | リクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token` |
| 検証失敗時のレスポンス | `BadRequest(400)` |

JSPにNablarchカスタムタグ（`n:form`等）を使用している場合、CSRFトークンは画面に自動で埋め込まれる（実装不要）。

#### カスタマイズが必要な場合

トークン名などを変更する場合は `WebConfig` で設定できる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- リクエストヘッダから取得する際のヘッダ名 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- リクエストパラメータから取得する際のパラメータ名 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <!-- セッションストアに格納する際のキー名 -->
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
</component>
```

**注意点**:
- `CsrfTokenVerificationHandler` はCSRFトークンをセッションストアに格納するため、**セッション変数保存ハンドラ（`SessionStoreHandler`）より後ろ**に配置すること。
- ログイン時にセッションIDのみを再生成する実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストア自体を破棄して再生成する実装であれば不要。
- リクエスト単体テスト時はCSRFトークンの検証が失敗するため、テスト設定でこのハンドラを `NopHandler` に差し替えて無効化すること。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

## 参照ナレッジ

- [CSRFトークンの生成と検証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンの生成と検証) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#制約) (s3)
- [CSRFトークンを再生成する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#csrfトークンを再生成する) (s5)
- [CSRF （クロスサイト・リクエスト・フォージェリ）](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md#csrf-クロスサイトリクエストフォージェリ) (s6)
- [ハンドラクラス名](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md#ハンドラクラス名) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the single expected fact: that adding the CSRF token verification handler (CsrfTokenVerificationHandler) to the handler configuration enables CSRF token generation and verification. The Actual Output explicitly states this in the conclusion ('CsrfTokenVerificationHandler をハンドラ構成に追加するだけで有効になる') and provides detailed supporting information about how the handler generates tokens (UUIDv4) and verifies them. The expected fact is fully present and not contradicted. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the question about preventing unauthorized POST requests from external sites and explaining Nablarch's CSRF protection mechanism and its configuration. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output is largely faithful to the retrieval context. The one flagged item regarding the ordering of the session store handler and CSRF handler is actually consistent with the retrieval context upon closer inspection — both agree that the session store handler must come before the CSRF handler. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う」は回答の「CsrfTokenVerificationHandler をハンドラ構成に追加するだけで有効になる」および詳細説明に含まれている |
| answer_relevancy | OK | 回答は質問「外部サイトからの不正POSTを防ぐCSRF対策の仕組みと設定方法」に直接答えており、CsrfTokenVerificationHandlerの設定方法・デフォルト動作・カスタマイズ・注意点を網羅している。質問と無関係な情報は含まれていない。 |
| faithfulness | OK | 回答のすべての主要な記述がナレッジMDと一致している。セッション変数保存ハンドラより後ろに配置する制約、UUIDv4によるトークン生成、GET/HEAD/TRACE/OPTIONSが検証対象外、X-CSRF-TOKENヘッダまたはcsrf-tokenパラメータからの取得、BadRequest(400)の返却、WebConfigでのカスタマイズ、CsrfTokenUtil.regenerateCsrfTokenの再生成条件、テスト時のNopHandler差し替えの方法はいずれもナレッジの記述と矛盾しない。 |

### 参照事実（expected_facts）

- CSRFトークン検証ハンドラをハンドラ構成に追加するとCSRFトークンの生成と検証を行う
