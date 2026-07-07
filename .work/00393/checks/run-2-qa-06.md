# qa-06 — run-2

## 質問

入力画面と確認画面のJSPを共通化して実装を減らす方法はあるか？

## 回答

**結論**: Nablarchカスタムタグの `confirmationPage` / `forInputPage` / `forConfirmationPage` タグを使うと、確認画面のJSPを1行（入力画面へのパス指定）に削減でき、入力フォームのカスタムタグ記述は入力・確認画面で完全に共通化できます。

**根拠**:

入力画面の JSP（通常の実装）

```jsp
<n:form>
  <div>
    <label>名前</label>
    <n:text name="form.name" />  <!-- 確認画面では自動的にテキスト表示になる -->
  </div>
  <div>
    <label>メール</label>
    <n:checkbox name="form.useMail" label="使用する" offLabel="使用しない" />
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>

  <!-- 入力画面と確認画面でボタンが異なる部分だけ分岐 -->
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

確認画面の JSP（これだけで完結）

```jsp
<!-- 入力画面のJSPへのパスを指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

各タグの役割：

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPから入力画面JSPをインクルードし、確認画面モードで描画 |
| `n:forInputPage` | 囲まれた内容を入力画面のみ表示 |
| `n:forConfirmationPage` | 囲まれた内容を確認画面のみ表示 |
| `n:ignoreConfirmation` | 確認画面でも入力フォームとして表示したい箇所に使用（例: チェックボックスをそのまま表示） |

`n:text` / `n:select` / `n:checkbox` などの入力系カスタムタグは、確認画面モードでは自動的に読み取り専用の表示（テキストのみ）に切り替わります。

**注意点**: 入力・確認画面で共通化できるのは「入力系のカスタムタグ」が対象です。`n:plainHidden` タグと `n:hiddenStore` タグは確認画面でも出力されます（画面間データ受け渡し用のため）。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

## 参照ナレッジ

- [入力画面と確認画面のJSPを共通化して実装を減らす](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面のjspを共通化して実装を減らす) (s3)
- [入力画面と確認画面を共通化する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面を共通化する) (s23)
- [confirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#confirmationpageタグ) (s64)
- [ignoreConfirmationタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#ignoreconfirmationタグ) (s65)
- [forInputPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forinputpageタグ) (s66)
- [forConfirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forconfirmationpageタグ) (s67)
- [カスタムタグの設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#カスタムタグの設定) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the core fact in the Expected Output: using the `confirmationPage` tag in the confirmation screen JSP to specify the path to the input screen JSP, enabling shared/common implementation. The Actual Output not only confirms this but provides detailed code examples, explains related tags, and elaborates on the mechanism. The single expected fact is fully present. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to share/unify JSP between input and confirmation screens to reduce implementation. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する」は回答の「確認画面の JSP（これだけで完結）`<n:confirmationPage path="./input.jsp" />`」および「`n:confirmationPage` | 確認画面JSPから入力画面JSPをインクルードし、確認画面モードで描画」に含まれている |
| answer_relevancy | OK | 回答のすべての内容（confirmationPageタグ、forInputPage/forConfirmationPageタグ、ignoreConfirmationタグ、plainHidden/hiddenStoreの例外動作）が「入力画面と確認画面のJSP共通化」という質問に直接答えており、的外れな情報は含まれていない。 |
| faithfulness | OK | 回答のJSPコード例はナレッジのlibaries-tag.md（行1585-1629）とほぼ同一。タグの役割説明もナレッジと一致。「入力・確認画面で共通化できるのは入力系のカスタムタグが対象」はナレッジの「入力・確認画面の表示制御は入力系のタグが対象」と一致。plainHidden/hiddenStoreが「確認画面でも出力される」という記述もナレッジのTip（「入力・確認画面ともに出力する」）と一致しており、矛盾はない。 |

### 参照事実（expected_facts）

- confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する
