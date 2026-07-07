# qa-06 — run-1

## 質問

入力画面と確認画面のJSPを共通化して実装を減らす方法はあるか？

## 回答

**結論**: NablarchのJakarta Server Pagesカスタムタグが提供する `n:confirmationPage`、`n:forInputPage`、`n:forConfirmationPage` の3タグを使うことで、入力画面と確認画面のJSPを共通化できます。確認画面JSPは入力画面JSPのパスを指定するだけで実装できます。

**根拠**:

入力画面のJSPに差分部分（ボタン切り替え等）を追加し、確認画面のJSPから `n:confirmationPage` で入力画面のJSPを参照します。

**入力画面のJSP（共通部分＋差分）**:
```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述を使用する -->
  <div>
    <label>名前</label>
    <n:text name="form.name" />
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
  <!-- ボタン表示のみ入力・確認画面で切り替え -->
  <div style="padding: 8px 0;">
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

**確認画面のJSP（これだけで実装完了）**:
```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

各タグの役割:

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPを取り込む（`path`属性でパス指定） |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 特定部分で確認画面向け表示を無効化したい場合に使用（例：確認画面でもチェック欄を表示したいとき） |

入力項目タグ（`n:text`、`n:checkbox`、`n:select` 等）は確認画面では自動的に値の表示（読み取り専用）に切り替わるため、同じJSP記述のまま動作します。

**注意点**: `plainHiddenタグ` と `hiddenStoreタグ` は入力・確認画面いずれでも出力されるため、この共通化の対象外となります。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

## 参照ナレッジ

- [入力画面と確認画面のJSPを共通化して実装を減らす](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面のjspを共通化して実装を減らす) (s3)
- [入力画面と確認画面を共通化する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#入力画面と確認画面を共通化する) (s23)
- [confirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#confirmationpageタグ) (s64)
- [ignoreConfirmationタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#ignoreconfirmationタグ) (s65)
- [forInputPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forinputpageタグ) (s66)
- [forConfirmationPageタグ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md#forconfirmationpageタグ) (s67)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the core fact from the Expected Output: using the `n:confirmationPage` tag in the confirmation screen JSP to specify the path to the input screen JSP for sharing/commonizing the JSP. The Actual Output provides extensive detail including code examples and table explanations, but the single key fact from the Expected Output—that `confirmationPage` tag is used on the confirmation page JSP with a path to the input page JSP for commonization—is explicitly and thoroughly present. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about how to share JSP between input and confirmation screens to reduce implementation. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.91 | NG | The score is 0.91 because the actual output omitted the `ignoreConfirmation` tag when describing the available tags, only mentioning three of the four tags (`confirmationPage`, `forInputPage`, and `forConfirmationPage`) referenced in the retrieval context. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する」は回答の「確認画面のJSP（これだけで実装完了）: `<n:confirmationPage path="./input.jsp" />`」およびタグ説明表の `n:confirmationPage` 行に明確に含まれている |
| answer_relevancy | OK | 回答は質問「入力画面と確認画面のJSPを共通化して実装を減らす方法」に直接答えており、n:confirmationPage、n:forInputPage、n:forConfirmationPageの3タグによる共通化手法をコード例・表形式で説明している。的外れな内容は含まれていない。 |
| faithfulness | OK | DeepEvalは「ignoreConfirmationタグが省略されている」としてNGを付けたが、回答の表（「各タグの役割」セクション）にn:ignoreConfirmationが4行目として明示されており、説明も「特定部分で確認画面向け表示を無効化したい場合に使用（例：確認画面でもチェック欄を表示したいとき）」とナレッジの記述と一致している。回答はナレッジの内容と矛盾しない。 |

### 参照事実（expected_facts）

- confirmationPageタグで確認画面のJSPに入力画面のJSPへのパスを指定して共通化する
