**結論**: 確認画面のJSPで `<n:confirmationPage>` タグを使用することで、入力画面と確認画面のJSPを共通化できます。確認画面側は1行の記述のみで済みます。

**根拠**:

入力項目のカスタムタグ（`n:text`、`n:checkbox`、`n:select` 等）は、確認画面でも入力画面と全く同じJSP記述のまま、確認画面向けの表示（値の表示のみ）に自動的に切り替わります。

共通化に使用する主なカスタムタグは以下の4つです。

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面のJSPで入力画面JSPのパスを指定 |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面で確認画面向けの変換を無効にしたい部分を囲む |

**入力画面のJSP**（そのまま確認画面でも使用される）:

```jsp
<n:form>
  <div>
    <label>名前</label>
    <n:text name="form.name" />       <!-- 確認画面では値表示になる -->
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan" listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>
  <!-- ボタンは画面ごとに切り替え -->
  <n:forInputPage>
    <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
  </n:forInputPage>
  <n:forConfirmationPage>
    <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
    <n:submit type="submit" uri="/action/sample/register" value="登録" />
  </n:forConfirmationPage>
</n:form>
```

**確認画面のJSP**（これだけで完結）:

```jsp
<n:confirmationPage path="./input.jsp" />
```

`path` 属性にフォワード先（入力画面）のJSPパスを指定するだけです。

**注意点**:
- `n:plainHidden` タグは入力・確認画面ともに同じ出力になります（画面間のデータ受け渡し用途のため）。
- `n:hiddenStore` タグも同様に、入力・確認画面ともに出力されます。
- チェックボックスのように確認画面でもチェック欄のまま表示したい場合は、`n:ignoreConfirmation` タグで囲むことで確認画面への変換を抑制できます。

参照: `component/libraries/libraries-tag.json#s23`、`component/libraries/libraries-tag-reference.json#s64`