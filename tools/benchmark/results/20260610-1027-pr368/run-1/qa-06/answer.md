**結論**: NablarchのJSPカスタムタグが提供する `n:confirmationPage`、`n:forInputPage`、`n:forConfirmationPage` を使うと、入力画面のJSPを確認画面と共通化できます。確認画面JSPは `n:confirmationPage` で入力画面JSPのパスを指定するだけで作成できます。

**根拠**:

入力画面のJSP (`input.jsp`) に、入力欄はそのまま共通記述し、画面固有のボタンだけを `n:forInputPage` / `n:forConfirmationPage` で切り分けます。

```jsp
<n:form>
  <!--
    入力欄は入力・確認画面で同じJSP記述を使用する。
    確認画面では自動的に読み取り専用の表示に切り替わる。
  -->
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

  <!-- ボタンは画面ごとに異なるので切り分ける -->
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

確認画面のJSP (`confirm.jsp`) は以下の1行だけで完成します。

```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

**使用するカスタムタグの役割:**

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPへのパスを指定し、共通化を有効にする |
| `n:forInputPage` | 囲まれた内容を入力画面でのみ表示する |
| `n:forConfirmationPage` | 囲まれた内容を確認画面でのみ表示する |
| `n:ignoreConfirmation` | 確認画面での読み取り専用表示を無効化したい箇所に使用する |

**注意点**: この共通化機能はクライアントのJavaScriptが必須です。また、入力項目の表示切り替え（入力欄→表示のみ）は入力系タグに対してのみ有効です。`n:plainHidden` と `n:hiddenStore` は入力・確認画面ともに出力されます。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67