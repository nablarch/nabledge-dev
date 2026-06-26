入力画面と確認画面のJSPを共通化するには、Nablarchのカスタムタグを使います。確認画面のJSPに `<n:confirmationPage path="./input.jsp" />` の1行を書くだけで、入力画面のJSPをそのまま確認画面として流用できます。

**結論**: `n:confirmationPage` タグを使うことで、入力画面のJSPを確認画面で再利用でき、重複した実装を大幅に削減できます。

---

**根拠**:

入力項目のカスタムタグ（`n:text`、`n:checkbox`、`n:select` 等）は、同じJSP記述のままで確認画面向けの表示に自動的に切り替わります。共通化に使用するタグは以下の4つです。

| タグ | 役割 |
|---|---|
| `n:confirmationPage` | 確認画面のJSPで入力画面JSPのパスを指定して共通化を有効化 |
| `n:forInputPage` | 入力画面でのみ表示したい部分（例：確認ボタン）を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分（例：戻る・登録ボタン）を囲む |
| `n:ignoreConfirmation` | 確認画面でも入力UI表示を維持したい部分に指定（例：チェックボックスを確認画面でもチェック欄で表示したい場合） |

**入力画面のJSP（input.jsp）**:
```jsp
<n:form>
  <!-- 入力欄は入力画面・確認画面で同じ記述 -->
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
  <!-- ボタンは画面によって切り替え -->
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

**確認画面のJSP（confirm.jsp）**:
```jsp
<!-- 入力画面のJSPへのパスを指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

---

**注意点**:
- `n:plainHidden` タグ（画面遷移の状態受け渡し用）および `n:hiddenStore` タグ（セッションストアのデータ受け渡し用）は、入力・確認画面のどちらでも出力されます。
- 入力～確認～完了画面間で入力情報を保持する場合、**複数タブ操作を許容しない**ときはDBストア、**許容する**ときはHIDDENストア（`n:hiddenStore` タグを使用）を選択してください。

---

参照: `libraries-tag.json:s23`, `libraries-session-store.json:s9`