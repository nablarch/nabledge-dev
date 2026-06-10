**結論**: Nablarchのカスタムタグ機能（`confirmationPage`タグ、`forInputPage`タグ、`forConfirmationPage`タグ）を使うことで、入力画面と確認画面のJSPを共通化できます。確認画面のJSPは入力画面JSPへのパスを指定するだけで実現できます。

**根拠**:

Nablarchのカスタムタグは「入力画面と確認画面のJSPを共通化する機能」を提供しており、入力画面向けに作成したJSPに差分（ボタン等）のみを追加するだけで確認画面を作成できます。

使用するタグ:

| タグ | 役割 |
|------|------|
| `<n:confirmationPage path="...">` | 確認画面のJSPに記述。入力画面JSPのパスを指定してフォワードする |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面でも入力モード表示を維持したい部分に使用（チェックボックスをチェック欄のまま表示する等） |

**入力画面のJSP**（入力欄はそのままで、ボタン部分だけ振り分け）:

```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述を使用 -->
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
  <!-- ボタンは入力・確認で振り分け -->
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

**確認画面のJSP**（入力画面のパスを指定するだけ）:

```jsp
<n:confirmationPage path="./input.jsp" />
```

入力系カスタムタグ（`n:text`、`n:select`、`n:checkbox` 等）は確認画面で自動的に値の表示モードに切り替わります。`plainHidden`タグと`hiddenStore`タグは入力・確認ともに出力されます。

**注意点**:
- 入力～確認～完了画面間の入力情報の保持にはセッションストアを使用します。複数タブを許容しない場合はDBストア、許容する場合はHIDDENストア（`hiddenStore`タグ）を使います。
- セッションストアにはFormではなくEntity（バリデーション済みオブジェクト）を格納することが推奨されます。

参照: component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s23, component/libraries/libraries-tag-reference.json:s64, component/libraries/libraries-tag-reference.json:s65, component/libraries/libraries-tag-reference.json:s66, component/libraries/libraries-tag-reference.json:s67, component/libraries/libraries-session-store.json:s9