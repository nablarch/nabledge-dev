**結論**: Nablarchのカスタムタグ（`n:confirmationPage`、`n:forInputPage`、`n:forConfirmationPage`）を使用することで、入力画面のJSPをそのまま確認画面に流用できます。確認画面のJSPには `n:confirmationPage` の1行のみ記述すれば済みます。

**根拠**:

入力画面と確認画面のJSPを共通化するには、以下のカスタムタグを使用します。

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面のJSPで入力画面のパスを指定し、入力画面JSPを読み込む |
| `n:forInputPage` | 入力画面でのみ表示したい部分（確認ボタンなど）を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分（戻る・登録ボタンなど）を囲む |
| `n:ignoreConfirmation` | 確認画面でも確認画面向け表示を無効化したい箇所（例：チェックボックスをそのまま表示したい場合）に使用 |

**入力画面のJSP（input.jsp）**:

```jsp
<n:form>
  <!-- 入力欄は入力画面と確認画面で同じJSP記述を使用する -->
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
  <!-- ボタンのみ入力画面と確認画面で切り替える -->
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

**確認画面のJSP（confirm.jsp）**:

```jsp
<!-- 入力画面のJSPへのパスを指定するだけでよい -->
<n:confirmationPage path="./input.jsp" />
```

確認画面側では `n:confirmationPage` タグで入力画面のパスを指定するだけです。入力系のカスタムタグ（`n:text`、`n:select` 等）は確認画面では自動的に読み取り専用の表示に切り替わります。

**注意点**: `n:plainHidden` タグと `n:hiddenStore` タグは、入力・確認画面の共通化においても両方のページで出力されます（画面間のデータ受け渡しに使用するため）。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

---