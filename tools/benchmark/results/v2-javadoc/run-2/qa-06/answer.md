Step 4でセクションを読み込み、Step 5〜8に進みます。

---

**結論**: Nablarchのカスタムタグが提供する `confirmationPageタグ`・`forInputPageタグ`・`forConfirmationPageタグ` を組み合わせることで、入力画面のJSPをそのまま確認画面でも使用でき、重複実装をなくせます。

**根拠**:

確認画面のJSPには `confirmationPage` タグで入力画面のJSPへのパスを指定するだけです。入力項目のカスタムタグ (`n:text`、`n:select`、`n:checkbox` など) は、確認画面状態のとき自動的に読み取り専用の表示に切り替わります。

入力画面のJSP（入力・確認で共用）:
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
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>

  <!-- 入力画面と確認画面でボタンを切り替える -->
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

確認画面のJSP（これだけでよい）:
```jsp
<n:confirmationPage path="./input.jsp" />
```

各タグの役割:

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPへのパスを指定。これにより入力画面のJSPが確認画面として描画される |
| `n:forInputPage` | ボディが入力画面でのみ表示される（確認ボタンなど） |
| `n:forConfirmationPage` | ボディが確認画面でのみ表示される（戻るボタン・登録ボタンなど） |
| `n:ignoreConfirmation` | 確認画面でも入力欄として表示したい部分（例：チェックボックスをそのまま見せたい場合）に指定する |

**注意点**: チェックボックス (`n:checkbox`) を確認画面でもチェック可能な入力欄として表示したい場合は `n:ignoreConfirmation` タグで囲む必要があります。

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67

---