セクションの内容を確認しました。回答を生成します。

---

**結論**: NablarchのカスタムタグとJSP共通化機能（`n:confirmationPage`タグ）を使うことで、入力画面のJSPをそのまま確認画面でも使い回せます。確認画面のJSPには入力画面へのパスを指定するだけで実装できます。

**根拠**:

入力・確認画面の共通化には以下の4つのタグを使用します。

| タグ | 役割 |
|---|---|
| `n:confirmationPage` | 確認画面JSPに記述し、入力画面JSPのパスを指定する |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面での確認表示を無効化したい部分に指定する |

**入力画面の JSP（`input.jsp`）**:
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
  <!-- ボタン表示だけ画面ごとに切り替える -->
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

**確認画面の JSP（`confirm.jsp`）**:
```jsp
<!-- 入力画面のJSPへのパスを指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

確認画面JSPには `n:confirmationPage` タグ1行を記述するだけで、入力系タグが自動的に確認画面向けの出力（テキスト表示）に切り替わります。

**注意点**:
- `n:plainHidden`タグと`n:hiddenStore`タグは画面状態の受け渡しを目的とするため、入力・確認画面の両方で出力されます（共通化の対象外）。
- チェックボックスなどで確認画面でもチェック欄をそのまま表示したい場合は `n:ignoreConfirmation` タグで確認画面向け変換を無効化できます。

参照: component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s23, component/libraries/libraries-tag-reference.json:s64, component/libraries/libraries-tag-reference.json:s65, component/libraries/libraries-tag-reference.json:s66, component/libraries/libraries-tag-reference.json:s67

---