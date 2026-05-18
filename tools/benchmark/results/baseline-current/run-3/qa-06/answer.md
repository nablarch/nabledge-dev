**結論**: Nablarchのカスタムタグを使って、入力画面のJSPをそのまま確認画面にも流用できます。確認画面のJSPには `<n:confirmationPage>` タグで入力画面のパスを指定するだけで、共通化が実現できます。

**根拠**:

入力・確認画面の共通化には以下の4つのカスタムタグを組み合わせます。

| タグ | 役割 |
|------|------|
| `<n:confirmationPage path="...">` | 確認画面JSPで入力画面JSPのパスを指定。これだけで共通化が成立 |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む（例：「確認」ボタン） |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む（例：「戻る」「登録」ボタン） |
| `<n:ignoreConfirmation>` | 確認画面での確認用表示を無効化（チェックボックスをそのまま表示したい場合など） |

実装例：

**入力画面のJSP（input.jsp）** — 入力欄はそのまま、ボタン部分だけ出し分け：
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
  <!-- ボタンは画面ごとに出し分ける -->
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

**確認画面のJSP（confirm.jsp）** — これだけでOK：
```jsp
<n:confirmationPage path="./input.jsp" />
```

**注意点**:
- 表示制御の対象は入力系タグ（`<n:text>`, `<n:checkbox>`, `<n:select>` など）です。
- `<n:plainHidden>` と `<n:hiddenStore>` は入力・確認画面の両方で出力されます（画面間のデータ受け渡し用途のため）。
- `<n:ignoreConfirmation>` を使うと、確認画面でも入力フォームとして表示できます（チェックボックスをそのまま見せたい場合など）。

参照: component/libraries/libraries-tag.json#s3, component/libraries/libraries-tag.json#s23, component/libraries/libraries-tag-reference.json#s64, component/libraries/libraries-tag-reference.json#s66, component/libraries/libraries-tag-reference.json#s67