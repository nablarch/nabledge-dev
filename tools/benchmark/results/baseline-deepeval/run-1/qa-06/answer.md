十分な情報が得られました。Step 5〜8を実行します。

---

**結論**: NablarchのJSPカスタムタグが提供する `confirmationPage` タグ・`forInputPage` タグ・`forConfirmationPage` タグを使うことで、入力画面のJSPをそのまま確認画面に流用でき、ボタンなどの差分のみを追加実装するだけで確認画面を作成できます。

**根拠**:

確認画面のJSPには `confirmationPage` タグで入力画面へのパスを指定するだけでよく、入力系カスタムタグは自動的に確認画面向けの出力（値の表示）に切り替わります。

**入力画面のJSP（入力・確認両用）**

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

**確認画面のJSP**

```jsp
<!--
  入力画面のJSPへのパスを指定する。
-->
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPはこれだけです。`confirmationPage` タグが内部でフォワードして入力画面のJSPをレンダリングしますが、その際に入力系タグは確認表示モードで動作します。

**使用するタグのまとめ**

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPに記述。入力画面JSPのパスを`path`属性に指定 |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面でも確認表示に切り替えずそのまま入力UIを出したい箇所に使用（チェックボックスをそのまま見せたい場合など）|

**注意点**:
- `plainHidden` タグと `hiddenStore` タグは、入力・確認どちらの画面でも出力されます（画面間のデータ受け渡し用途のため）。
- 入力〜確認〜完了画面間でのデータ保持には、セッションストアを使います。複数タブを許容しない場合はDBストア、許容する場合はHIDDENストアを使用します。セッションストアにはEntityを格納し、Formを直接格納しないことが推奨されています。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67, libraries-session-store.json:s9

---