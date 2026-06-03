Step 4の`read_sections`は上記で取得済みです。答えを生成します。

---

**結論**: NablarchのJSPカスタムタグ機能を使うと、確認画面のJSPで `<n:confirmationPage path="..." />` だけを記述し、入力画面のJSPを読み込む形で共通化できます。入力画面との差分（ボタンなど）は `<n:forInputPage>` / `<n:forConfirmationPage>` タグで制御します。

**根拠**:

使用する4つのカスタムタグ：

| タグ | 役割 |
|---|---|
| `n:confirmationPage` | 確認画面JSPから入力画面JSPへのパスを指定し、入力項目を確認画面用出力に切り替える |
| `n:forInputPage` | 入力画面でのみ表示したいブロックを囲む（例：「確認」ボタン） |
| `n:forConfirmationPage` | 確認画面でのみ表示したいブロックを囲む（例：「戻る」「登録」ボタン） |
| `n:ignoreConfirmation` | 確認画面での確認画面向け表示を無効化したい箇所（例：確認画面でもチェックボックスをそのまま表示したい場合）に使用 |

**入力画面のJSP**（入力欄はそのまま、ボタンのみ分岐）:

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

**確認画面のJSP**（入力画面へのパスを指定するだけ）:

```jsp
<n:confirmationPage path="./input.jsp" />
```

**注意点**: 入力・確認画面の表示制御は入力系タグが対象です。ただし `n:plainHidden`（画面間の状態受け渡し用）と `n:hiddenStore`（セッションストアのデータ受け渡し用）は例外で、入力・確認画面ともに出力されます。

参照: component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s23, component/libraries/libraries-tag-reference.json:s64, component/libraries/libraries-tag-reference.json:s66, component/libraries/libraries-tag-reference.json:s67

---