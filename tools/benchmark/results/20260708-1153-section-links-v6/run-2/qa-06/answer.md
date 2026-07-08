**結論**: NablarchのJakarta Server PagesカスタムタグはJSP共通化機能を提供しており、`confirmationPageタグ`・`forInputPageタグ`・`forConfirmationPageタグ`の3つを組み合わせることで、入力画面と確認画面のJSPを共通化できます。

**根拠**:

入力系のカスタムタグ（`n:text`、`n:checkbox`、`n:select` など）は、入力画面と全く同じJSP記述のまま確認画面用の出力もできます。画面ごとの差分（ボタン等）のみを追加実装するだけで確認画面を作成できます。

**実装手順**:

1. **入力画面のJSP**：入力欄は共通のカスタムタグで記述し、ボタン部分だけ `n:forInputPage` / `n:forConfirmationPage` で切り替える

```jsp
<n:form>
  <!--
    入力欄は、入力画面と確認画面で同じJSP記述を使用する。
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
  <!--
   ボタン表示は、入力画面と確認画面で異なるので、
   forInputPageタグとforConfirmationPageタグを使用する。
  -->
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

2. **確認画面のJSP**：`n:confirmationPage` タグに入力画面JSPのパスを指定するだけ

```jsp
<!--
  入力画面のJSPへのパスを指定する。
-->
<n:confirmationPage path="./input.jsp" />
```

**使用するタグ一覧**:

| タグ | 用途 |
|---|---|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPへのパスを指定（`path`属性） |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面で確認画面向けの表示を無効化したい部分（例：チェックボックスをそのまま表示したい場合） |

**注意点**:

- `n:plainHidden`タグと`n:hiddenStore`タグは、画面間でデータを受け渡す目的のため入力・確認画面ともに出力される（forInputPage/forConfirmationPageの制御対象外）
- 入力・確認画面の表示制御は入力系のタグが対象となる

参照:
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  入力画面と確認画面のJSPを共通化して実装を減らす
  入力画面と確認画面を共通化する
- タグリファレンス
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md
  confirmationPageタグ
  forInputPageタグ
  forConfirmationPageタグ
  ignoreConfirmationタグ