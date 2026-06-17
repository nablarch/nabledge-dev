**結論**: Nablarchのカスタムタグ機能を使うと、入力画面と確認画面のJSPを共通化できます。確認画面のJSPには `<n:confirmationPage path="./input.jsp" />` の1行を記述するだけで、入力画面のJSPが確認画面用に自動変換されて表示されます。

**根拠**: 入力画面と確認画面の共通化には以下の4つのカスタムタグを使用します。

**`<n:confirmationPage>`** — 確認画面のJSPで入力画面のJSPパスを指定します。これにより、入力項目（`<n:text>` など）が自動で確認画面向けの表示（テキスト出力）に切り替わります。

**`<n:forInputPage>`** — 入力画面でのみ表示したい部分（例：「確認」ボタン）を囲みます。

**`<n:forConfirmationPage>`** — 確認画面でのみ表示したい部分（例：「戻る」「登録」ボタン）を囲みます。

**`<n:ignoreConfirmation>`** — 確認画面でも確認画面向け変換を無効にしたい部分に指定します（例：確認画面でもチェックボックスのチェック欄を表示したい場合）。

実装例:

```jsp
<%-- 入力画面 (input.jsp) --%>
<n:form>
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

```jsp
<%-- 確認画面 (confirm.jsp) --%>
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPはこの1行だけで完結します。入力画面のJSPが読み込まれ、`<n:text>` などの入力タグが自動でテキスト出力に変換されます。

参照: component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s23