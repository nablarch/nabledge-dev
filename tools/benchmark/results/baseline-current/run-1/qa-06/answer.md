**結論**: Nablarch のカスタムタグ機能を使うことで、入力画面と確認画面のJSPを1ファイルに共通化できます。確認画面JSPには `<n:confirmationPage>` タグで入力画面JSPへのパスを指定するだけで実現できます。

**根拠**:

Nablarchのカスタムタグは「入力画面と確認画面のJSP共通化」機能を提供しています。使用するタグは以下の4つです。

| タグ | 用途 |
|------|------|
| `<n:confirmationPage path="...">` | 確認画面JSPで入力画面JSPへのパスを指定し、共通化を行う |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面で確認向け表示を無効化したい部分に指定する（チェックボックスをそのまま表示したい場合など） |

**実装例**:

入力画面のJSP（`input.jsp`）:
```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じ記述をそのまま使用 -->
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

  <!-- ボタンは入力・確認で異なるため forInputPage / forConfirmationPage で切り替え -->
  <n:forInputPage>
    <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
  </n:forInputPage>
  <n:forConfirmationPage>
    <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
    <n:submit type="submit" uri="/action/sample/register" value="登録" />
  </n:forConfirmationPage>
</n:form>
```

確認画面のJSP（`confirm.jsp`）:
```jsp
<!-- これだけでOK。入力画面JSPをそのまま確認画面として描画する -->
<n:confirmationPage path="./input.jsp" />
```

**注意点**:
- `<n:plainHidden>` と `<n:hiddenStore>` は共通化対象外で、入力・確認画面ともに出力されます（画面間でのデータ受け渡し用途のため）
- 共通化が適用されるのは入力系のカスタムタグのみです（表示用タグは対象外）
- 確認画面でもチェックボックスをそのまま表示したい場合は `<n:ignoreConfirmation>` で確認画面向け変換を無効化できます

参照: `component/libraries/libraries-tag.json#s3`, `component/libraries/libraries-tag.json#s23`, `component/libraries/libraries-tag-reference.json#s64`, `component/libraries/libraries-tag-reference.json#s66`, `component/libraries/libraries-tag-reference.json#s67`