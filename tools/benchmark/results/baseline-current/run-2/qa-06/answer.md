**結論**: `n:confirmationPage` タグを使用することで、入力画面のJSPをそのまま確認画面に流用でき、実装量を大幅に削減できます。

**根拠**:

Nablarchのカスタムタグライブラリには、入力画面と確認画面を共通化するための4つのタグが用意されています。

**基本的な使い方**

確認画面のJSP (`confirm.jsp`) は以下の1行だけで作成できます：

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<!-- 登録画面を確認画面に変換して表示する -->
<n:confirmationPage path="./create.jsp" ></n:confirmationPage>
```

`n:confirmationPage` タグの `path` 属性に入力画面JSPのパスを指定するだけで、入力タグが自動的に確認画面用の表示（読み取り専用ラベル）に変換されます。

**入力画面側の出し分け**

入力画面のJSP (`create.jsp`) では、表示条件に応じて以下のタグで囲みます：

```jsp
<div class="button-nav">
    <!-- 登録ボタンは入力画面でのみ表示 -->
    <n:forInputPage>
        <n:button uri="/action/client/confirm"
                  cssClass="btn btn-lg btn-success">登録</n:button>
    </n:forInputPage>
    <!-- 戻るボタン・確定ボタンは確認画面でのみ表示 -->
    <n:forConfirmationPage>
        <n:button uri="/action/client/back"
                  cssClass="btn btn-lg btn-light">入力へ戻る</n:button>
        <n:button uri="/action/client/create"
                  cssClass="btn btn-lg btn-success">確定</n:button>
    </n:forConfirmationPage>
</div>
```

**使用するタグの一覧**

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面パスを指定。入力タグを確認表示に変換 |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面でも確認モード変換を無効化したい部分に指定（チェックボックスをそのまま表示したい場合など） |

**注意点**:
- `n:confirmationPage` の `path` 属性には入力画面JSPへのパスを指定します（動的属性は使用不可）
- `n:forInputPage`、`n:forConfirmationPage`、`n:ignoreConfirmation` はいずれも属性なしで使用します
- `n:text` や `n:select` などの入力項目タグは、確認画面モードでは自動的に読み取り専用表示に切り替わります

参照: `component/libraries/libraries-tag.json#s3`, `component/libraries/libraries-tag.json#s23`, `component/libraries/libraries-tag-reference.json#s64`, `processing-pattern/web-application/web-application-client-create2.json`