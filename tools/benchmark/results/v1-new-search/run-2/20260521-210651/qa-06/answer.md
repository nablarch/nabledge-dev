**結論**: NablarchのJSPカスタムタグが提供する `n:confirmationPage`、`n:forInputPage`、`n:forConfirmationPage`、`n:ignoreConfirmation` の4タグを組み合わせることで、入力画面と確認画面のJSPを共通化できます。確認画面のJSPは `<n:confirmationPage path="./input.jsp" />` の1行のみで済みます。

**根拠**:

入力画面のJSPにこれらのタグを使って差分（ボタン等）を記述し、確認画面のJSPから入力画面のJSPをインクルードする形をとります。入力系タグは確認画面では自動的に読み取り専用表示に切り替わります。

```jsp
<!-- 入力画面のJSP（input.jsp）-->
<n:form>
  <!-- 入力欄は入力画面・確認画面で同一のJSP記述を使用 -->
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
  <!-- ボタンは画面ごとに異なるので forInputPage / forConfirmationPage で切り替え -->
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

```jsp
<!-- 確認画面のJSP（confirm.jsp）— これだけでOK -->
<n:confirmationPage path="./input.jsp" />
```

各タグの役割:

| タグ | 説明 |
|---|---|
| `n:confirmationPage` | 確認画面のJSPで入力画面のJSPパスを指定してインクルードする。`path`属性に入力画面のパスを指定する |
| `n:forInputPage` | 入力画面でのみ表示したい部分（例: 「確認」ボタン）を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分（例: 「戻る」「登録」ボタン）を囲む |
| `n:ignoreConfirmation` | 確認画面での読み取り専用化を無効化したい箇所（例: チェックボックスをそのまま表示したい場合）に使用する |

**注意点**:
- `n:plainHidden` タグと `n:hiddenStore` タグは、入力・確認画面のどちらにも出力される（画面状態の受け渡し用のため）。
- チェックボックス等で確認画面でも入力状態のまま表示したい場合は `n:ignoreConfirmation` で囲む。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

---