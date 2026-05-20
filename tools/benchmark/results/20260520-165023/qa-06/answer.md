**結論**: NablarchのJSPカスタムタグ（`confirmationPageタグ`・`forInputPageタグ`・`forConfirmationPageタグ`）を使うことで、入力画面のJSPをそのまま確認画面に流用できます。確認画面JSPは1行の `<n:confirmationPage>` タグを記述するだけです。

**根拠**:

入力画面のJSP（例: `input.jsp`）では、共通のフォーム部品は通常どおり記述し、画面ごとに差異があるボタン等を `forInputPage` / `forConfirmationPage` タグで振り分けます。

```jsp
<%-- 入力画面のJSP (input.jsp) --%>
<n:form>
  <%-- 入力欄は入力画面・確認画面で同じJSP記述 --%>
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

  <%-- ボタンは画面ごとに異なるため振り分け --%>
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

確認画面のJSPは入力画面JSPへのパスを指定するだけです。

```jsp
<%-- 確認画面のJSP (confirm.jsp) --%>
<n:confirmationPage path="./input.jsp" />
```

確認画面では、入力項目のカスタムタグ（`n:text` 等）が自動的に読み取り専用の表示に切り替わります。

使用するカスタムタグの役割:

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPから入力画面JSPを指定して共通化 |
| `n:forInputPage` | 入力画面のみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面のみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面でも入力UI（チェックボックスなど）のまま表示したい部分に使う |

**注意点**: 二重サブミット防止のトークン（`useToken`）は、入力画面と確認画面を共通化した場合、確認画面ではデフォルトで `true` になるため、`formタグ` に明示的に指定する必要はありません。

参照: `component/libraries/libraries-tag.json:s23`