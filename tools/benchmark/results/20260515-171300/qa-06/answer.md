**結論**: 入力画面と確認画面のJSPを共通化することは可能です。Nablarchカスタムタグの `confirmationPage` タグを使用することで、入力画面用に作成したJSPを確認画面でそのまま流用できます。

**根拠**:

Nablarchのカスタムタグライブラリは、入力画面と確認画面のJSP共通化をサポートする以下のタグを提供しています。

**① confirmationPage タグ（確認画面JSP用）**

確認画面のJSPで入力画面JSPへのパスを指定するだけで共通化が実現します。

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<n:confirmationPage path="./input.jsp" />
```

**② forInputPage タグ／forConfirmationPage タグ（表示切り替え）**

入力画面・確認画面でそれぞれ表示したい要素を出し分けできます。

```jsp
<n:forInputPage>
    <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
</n:forInputPage>
<n:forConfirmationPage>
    <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
    <n:submit type="submit" uri="/action/sample/register" value="登録" />
</n:forConfirmationPage>
```

**③ ignoreConfirmation タグ**

確認画面で確認画面向けの自動変換を無効化したい部分に使用します。

**実装例（登録確認画面のJSP）**:

```jsp
<n:confirmationPage path="./create.jsp" ></n:confirmationPage>
```

入力系タグ（`n:text`、`n:select` 等）は、確認画面では自動的にラベル表示に切り替わります。

**注意点**:
- `plainHidden` タグと `hiddenStore` タグは入力・確認画面の両方で出力されます（画面遷移での状態受け渡しに使用するため）。
- `forInputPage`/`forConfirmationPage` で入力・確認それぞれに異なるボタンを表示するのが推奨パターンです。
- 共通化した場合、確認画面では `useToken` 属性のデフォルトが `true` になるため、二重サブミット防止の設定は別途不要です。

参照: `libraries-tag.json#s3`, `libraries-tag.json#s23`, `processing-pattern/web-application/web-application-client-create2.json`