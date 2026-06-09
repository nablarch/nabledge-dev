**結論**: Nablarchカスタムタグの `confirmationPage` タグ、`forInputPage` タグ、`forConfirmationPage` タグを組み合わせることで、入力画面のJSPをそのまま確認画面でも使用でき、重複実装を排除できます。

**根拠**:

確認画面のJSP（`confirm.jsp`）には `confirmationPage` タグで入力画面のパスを指定するだけです。

```jsp
<!-- 確認画面のJSP -->
<n:confirmationPage path="./input.jsp" />
```

入力画面のJSP（`input.jsp`）は入力欄の記述はそのままに、画面ごとに出し分けたい部分（ボタンなど）を `forInputPage` / `forConfirmationPage` タグで囲みます。

```jsp
<n:form>
  <!-- 入力欄は入力画面・確認画面で同じ記述を使用する -->
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

  <!-- ボタンは画面によって異なるので出し分ける -->
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

使用するカスタムタグの役割：

| タグ | 役割 |
|---|---|
| `n:confirmationPage` | 確認画面のJSPで入力画面JSPのパスを指定し、共通化を有効化する |
| `n:forInputPage` | ボディ内のコンテンツを入力画面のみ出力する |
| `n:forConfirmationPage` | ボディ内のコンテンツを確認画面のみ出力する |
| `n:ignoreConfirmation` | 確認画面でも入力画面と同じ表示にしたい部分（例：チェックボックスをそのまま表示したい場合など）に指定する |

**注意点**:
- `plainHidden` タグと `hiddenStore` タグは入力・確認画面ともに出力されます（これは画面間のデータ受け渡し用途のため意図的な動作）。
- `confirmationPage` タグが指定された場合、`form` タグの `useToken` 属性のデフォルトが `true` になります（二重サブミット防止トークンが自動的に有効化される）。

参照: `component/libraries/libraries-tag.json:s3`, `component/libraries/libraries-tag.json:s23`, `component/libraries/libraries-tag-reference.json:s64`, `component/libraries/libraries-tag-reference.json:s65`, `component/libraries/libraries-tag-reference.json:s66`, `component/libraries/libraries-tag-reference.json:s67`, `component/libraries/libraries-tag-reference.json:s6`