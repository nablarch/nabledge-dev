ウェブアプリケーションでは、Nablarch のカスタムタグを使用することで、入力画面と確認画面の JSP を共通化できます。

## 仕組み

入力項目のカスタムタグ（`<n:text>`、`<n:checkbox>`、`<n:select>` など）は、入力画面と全く同じ JSP 記述のまま、確認画面用の出力（読み取り専用表示）を自動的に行います。そのため、入力画面の JSP をそのまま確認画面でも使い回せます。

## 使用するカスタムタグ

| タグ | 用途 |
|---|---|
| `<n:confirmationPage path="..." />` | 確認画面の JSP から入力画面の JSP を参照する（確認画面 JSP はこの1行のみで実装できる） |
| `<n:forInputPage>` | 入力画面でのみ表示したいコンテンツ（例：「確認」ボタン）を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したいコンテンツ（例：「戻る」「登録」ボタン）を囲む |
| `<n:ignoreConfirmation>` | 確認画面でも入力 UI をそのまま表示したい部分に指定する（例：チェックボックスをチェック欄のまま表示したい場合） |

## 実装例

**入力画面の JSP（`input.jsp`）**

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
  <div>
    <%-- 入力画面にのみ表示 --%>
    <n:forInputPage>
      <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
    </n:forInputPage>
    <%-- 確認画面にのみ表示 --%>
    <n:forConfirmationPage>
      <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
      <n:submit type="submit" uri="/action/sample/register" value="登録" />
    </n:forConfirmationPage>
  </div>
</n:form>
```

**確認画面の JSP（`confirm.jsp`）**

```jsp
<%-- 入力画面の JSP へのパスを1行指定するだけ --%>
<n:confirmationPage path="./input.jsp" />
```

確認画面の JSP は `<n:confirmationPage>` の1行のみで実装できます。これにより、確認画面では `input.jsp` が確認モードで読み込まれ、入力項目がすべて読み取り専用で表示されます。

## 補足：入力・確認画面の両方で出力されるタグ

通常の入力項目とは異なり、以下のタグは入力画面・確認画面の両方で出力されます。

- **`<n:plainHidden>`** — 画面遷移の状態など、画面間でデータを受け渡す目的で使用するため、両画面で出力されます。
- **`<n:hiddenStore>`** — セッションストアのデータを画面間で受け渡すために使用するため、両画面で出力されます。