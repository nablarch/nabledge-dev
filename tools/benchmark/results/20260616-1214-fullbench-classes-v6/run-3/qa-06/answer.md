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