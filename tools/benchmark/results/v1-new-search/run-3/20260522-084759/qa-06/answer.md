**結論**: Nablarchカスタムタグの `<n:confirmationPage>` タグを使うことで、入力画面と確認画面のJSPを共通化できる。確認画面のJSPには `path` 属性で入力画面のJSPパスを指定するだけでよく、入力画面のJSP記述をそのまま再利用できる。

**根拠**:

カスタムタグライブラリには、入力画面と確認画面を共通化するための以下の4つのタグが提供されている。

| タグ | 用途 |
|---|---|
| `<n:confirmationPage path="...">` | 確認画面のJSPに記述し、入力画面のJSPパスを指定 |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面で確認画面向け表示を無効化したい部分に使用（例：チェックボックスをそのまま表示したい場合） |

入力項目のカスタムタグ（`<n:text>`、`<n:select>`、`<n:checkbox>` 等）は、確認画面モードでは自動的に値の表示専用出力に切り替わる。

**実装例**:

入力画面のJSP（`input.jsp`）：

```jsp
<n:form>
  <!-- 入力欄は入力画面・確認画面で同じJSP記述を使用する -->
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
  <!-- ボタン部分だけ入力画面と確認画面で切り替える -->
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

確認画面のJSP（`confirm.jsp`）：

```jsp
<!-- 入力画面のJSPパスを指定するだけでよい -->
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPには `<n:confirmationPage>` の1行を記述するだけで、入力画面のJSP内容が確認画面モードで表示される。

**注意点**:
- `<n:plainHidden>` タグと `<n:hiddenStore>` タグは入力・確認画面の両方で出力される（画面間のデータ受け渡し用のため）。
- `<n:ignoreConfirmation>` タグで囲んだ部分は確認画面でも入力画面と同じ表示となる（チェックボックスをそのまま表示したい場合などに使用）。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

---