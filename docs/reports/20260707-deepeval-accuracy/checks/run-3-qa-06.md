# qa-06 — run-3

## 質問

入力画面と確認画面のJSPを共通化して実装を減らす方法はあるか？

## 回答

**結論**: NablarchのJakarta Server Pagesカスタムタグを使用すると、`confirmationPage`タグを確認画面のJSPに1行記述するだけで入力画面のJSPを確認画面として流用でき、入力/確認画面のJSPを共通化できます。

**根拠**:

入力画面のJSPはそのまま使い、確認画面のJSPには以下を記述するだけです。

```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

入力画面のJSPで、入力画面と確認画面で表示を変えたい箇所（ボタンなど）は `forInputPage`タグ・`forConfirmationPage`タグで切り替えます。

```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述を使用 -->
  <div>
    <label>名前</label>
    <n:text name="form.name" />
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>

  <!-- ボタン表示は入力・確認画面で切り替える -->
  <div>
    <n:forInputPage>
      <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
    </n:forInputPage>
    <n:forConfirmationPage>
      <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
      <n:submit type="submit" uri="/action/sample/register" value="登録" />
    </n:forConfirmationPage>
  </div>
</n:form>
```

使用するカスタムタグの役割:

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面のJSPで入力画面のJSPパスを指定 |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面でも確認モードを無効化したい部分に使用（例：チェックボックスをそのまま表示する場合） |

**注意点**: 入力項目タグ（`n:text`、`n:select`など）は確認画面では自動的に読み取り専用表示に切り替わります。ただし `plainHiddenタグ` と `hiddenStoreタグ` は入力・確認画面ともに出力されます。

参照: libraries-tag.json:s23, libraries-tag.json:s3

## 参照ナレッジ

- [入力画面と確認画面を共通化する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面を共通化する) (s23)
- [入力画面と確認画面のJSPを共通化して実装を減らす](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面のjspを共通化して実装を減らす) (s3)
- [confirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#confirmationpageタグ) (s64)
- [forInputPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forinputpageタグ) (s66)
- [forConfirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forconfirmationpageタグ) (s67)
- [ignoreConfirmationタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#ignoreconfirmationタグ) (s65)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the core fact in the Expected Output: using the `confirmationPage` tag in the confirmation page's JSP to specify the path to the input page's JSP, thereby sharing/commonizing the JSPs. The Actual Output not only confirms this fact but provides detailed explanation, code examples, and additional related information. The single expected fact is clearly and accurately represented. |
| answer_relevancy | 0.95 | 0.94 | NG | The score is 0.94 because the response is highly relevant and addresses the question about how to share JSP between input and confirmation screens to reduce implementation. It loses a small amount of points due to including a reference/citation entry that does not contribute substantively to answering the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する」は回答の「confirmationPageタグを確認画面のJSPに1行記述するだけで入力画面のJSPを確認画面として流用でき」および `<n:confirmationPage path="./input.jsp" />` のコード例に含まれている |
| answer_relevancy | OK | 回答は「入力画面と確認画面のJSPを共通化する方法」という質問に直接答えており、confirmationPageタグの使い方、コード例、関連タグ一覧表、注意点の全てが質問に関連する内容である。DeepEvalが指摘した「参照: libraries-tag.json:s23, libraries-tag.json:s3」という末尾の内部参照メモは回答の本質を損なうものではなく、的外れな内容とは言えない。 |
| faithfulness | OK | confirmationPageタグの説明、forInputPage/forConfirmationPageタグの説明、ignoreConfirmationタグの説明、plainHiddenタグとhiddenStoreタグが入力・確認画面ともに出力される旨は全てナレッジ(libraries-tag.md)の記述と一致している。「入力項目タグは確認画面では自動的に読み取り専用表示に切り替わる」という記述も、ナレッジが「確認画面向けを出力できる」かつignoreConfirmationタグが「確認画面向けの表示を無効化」するために存在することと矛盾しない。 |

### 参照事実（expected_facts）

- confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する
