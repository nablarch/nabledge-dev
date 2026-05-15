**結論**: `n:confirmationPage` タグを使い、確認画面JSPから入力画面JSPのパスを指定することで、JSPを共通化できます。

**根拠**:

Nablarchのカスタムタグには入力画面と確認画面を共通化する機能が用意されています。確認画面のJSPは以下のように1行で実装できます。

**確認画面のJSP（例: confirm.jsp）**
```jsp
<n:confirmationPage path="./create.jsp" />
```

入力画面のJSP（`create.jsp`）はそのまま流用でき、入力系タグ（`n:text`, `n:select`, `n:checkbox` など）は自動的にラベル表示に切り替わります。

**入力画面と確認画面で表示を出し分けたい場合**は、以下のタグで制御します。

```jsp
<!-- 入力画面のみ表示したい部分 -->
<n:forInputPage>
    <n:button uri="/action/client/confirm">登録</n:button>
</n:forInputPage>

<!-- 確認画面のみ表示したい部分 -->
<n:forConfirmationPage>
    <n:button uri="/action/client/back">入力へ戻る</n:button>
    <n:button uri="/action/client/create">確定</n:button>
</n:forConfirmationPage>
```

利用できるタグの一覧：

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPのパスを指定 |
| `n:forInputPage` | 入力画面のみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面のみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面で確認モードの表示を無効化する部分に指定（例: チェックボックスを入力状態のまま表示したい場合） |

**注意点**:
- `n:plainHidden` と `n:hiddenStore` タグは、画面遷移の状態を受け渡す用途のため、入力・確認画面ともに出力されます（共通化の対象外）。
- 確認画面のアクションメソッドでは、業種リストなど画面表示に必要なデータをリクエストスコープに再セットする必要があります（`n:select` など、リストを参照するタグの表示に必要なため）。
- 入力情報は `SessionUtil` を使ってセッションストアに保存します。フォームクラスではなくエンティティに変換してから保存してください（フォームはセッションストアに格納しない）。

参照: `component/libraries/libraries-tag.json#s3`, `component/libraries/libraries-tag.json#s23`, `processing-pattern/web-application/web-application-client-create2.json`