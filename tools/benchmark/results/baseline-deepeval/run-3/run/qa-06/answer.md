**結論**: NablarchのJSPカスタムタグを使用することで、入力画面のJSPをそのまま確認画面にも流用できます。確認画面のJSPには `<n:confirmationPage>` タグでパスを指定するだけで、入力画面と確認画面を共通化できます。

**根拠**:

入力系のカスタムタグは、入力画面と同じJSP記述のまま確認画面用の表示を出力できます。以下の4つのタグを組み合わせて使います。

| タグ | 用途 |
|---|---|
| `<n:confirmationPage>` | 確認画面のJSPに記述。入力画面のJSPパスを指定してフォワード |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面でも確認画面向け表示を無効化したい部分に使用 |

**入力画面のJSP（input.jsp）**:

```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述 -->
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
  <!-- ボタン表示は画面によって切り替える -->
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
<!-- 入力画面のJSPへのパスを指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPは `<n:confirmationPage>` タグ1行のみで済み、入力画面のJSPをインクルード・再利用します。

**注意点**:

- `<n:plainHidden>` と `<n:hiddenStore>` タグは入力・確認画面ともに出力されます（画面間データ受け渡し用途のため）
- `<n:ignoreConfirmation>` はチェックボックスなど確認画面でもチェック欄を表示したい場合に使用します

参照: component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s23, component/libraries/libraries-tag-reference.json:s64, component/libraries/libraries-tag-reference.json:s66, component/libraries/libraries-tag-reference.json:s67

---