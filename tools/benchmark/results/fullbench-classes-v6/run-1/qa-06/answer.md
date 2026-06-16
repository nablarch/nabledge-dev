**結論**: NablarchのJakarta Server Pagesカスタムタグが提供する `n:confirmationPage`、`n:forInputPage`、`n:forConfirmationPage` の3タグを使うことで、入力画面と確認画面のJSPを共通化できます。確認画面JSPは入力画面JSPのパスを指定するだけで実装できます。

**根拠**:

入力画面のJSPに差分部分（ボタン切り替え等）を追加し、確認画面のJSPから `n:confirmationPage` で入力画面のJSPを参照します。

**入力画面のJSP（共通部分＋差分）**:
```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述を使用する -->
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
  <!-- ボタン表示のみ入力・確認画面で切り替え -->
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

**確認画面のJSP（これだけで実装完了）**:
```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

各タグの役割:

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPを取り込む（`path`属性でパス指定） |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 特定部分で確認画面向け表示を無効化したい場合に使用（例：確認画面でもチェック欄を表示したいとき） |

入力項目タグ（`n:text`、`n:checkbox`、`n:select` 等）は確認画面では自動的に値の表示（読み取り専用）に切り替わるため、同じJSP記述のまま動作します。

**注意点**: `plainHiddenタグ` と `hiddenStoreタグ` は入力・確認画面いずれでも出力されるため、この共通化の対象外となります。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67