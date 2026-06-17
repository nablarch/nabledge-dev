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