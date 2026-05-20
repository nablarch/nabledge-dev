**結論**: Nablarchカスタムタグの `confirmationPage` タグ、`forInputPage` タグ、`forConfirmationPage` タグを使うことで、入力画面のJSPを確認画面と共通化できます。確認画面のJSPには1行の `<n:confirmationPage path="...">` を書くだけで済みます。

**根拠**:

使用するカスタムタグは以下の4つです。

| タグ | 用途 |
|---|---|
| `<n:confirmationPage path="...">` | 確認画面のJSP内で入力画面JSPのパスを指定して共通化を行う |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面でも入力UIのまま表示したい部分に使う（例：チェックボックスなど） |

**入力画面のJSP（input.jsp）**

入力項目部分はそのまま共通として書き、ボタンだけ `forInputPage` / `forConfirmationPage` で分岐させます。

```jsp
<n:form>
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

**確認画面のJSP（confirm.jsp）**

```jsp
<n:confirmationPage path="./input.jsp" />
```

これだけで確認画面が完成します。`n:text`、`n:select`、`n:checkbox` などの入力系タグは、確認画面時は自動的に読み取り専用の表示（テキスト出力）に切り替わります。

**注意点**:
- `plainHiddenタグ` と `hiddenStoreタグ` は入力・確認画面ともに出力されます（画面間データ受け渡し用のため）。
- `ignoreConfirmationタグ` を使うと、確認画面でも入力UIのまま表示したい部分（例：チェックボックスをチェック可能にしたい）を個別に指定できます。

参照: component/libraries/libraries-tag.json:s23, component/libraries/libraries-tag.json:s3