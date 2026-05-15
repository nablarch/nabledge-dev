**結論**: Nablarch のカスタムタグを使うことで、入力画面と確認画面の JSP を共通化できます。入力画面の JSP をベースに、差分（ボタン等）だけを追加実装するだけで確認画面を作成できます。

**根拠**:

以下の4つのカスタムタグを組み合わせて共通化を実現します。

| タグ | 用途 |
|---|---|
| `confirmationPage` | 確認画面 JSP で入力画面 JSP のパスを指定し、共通化を有効にする |
| `forInputPage` | 入力画面でのみ表示したい部分（例：入力用ボタン）を囲む |
| `forConfirmationPage` | 確認画面でのみ表示したい部分（例：確認用ボタン）を囲む |
| `ignoreConfirmation` | 確認画面でも確認画面向けの変換を無効化したい部分に使用する（例：チェックボックスをそのまま表示したい場合） |

**基本的な実装パターン**:

確認画面の JSP で `confirmationPage` タグに入力画面のパスを指定するだけで、入力系タグが自動的に確認画面用の出力に切り替わります。

```jsp
<%-- 確認画面 JSP --%>
<n:confirmationPage path="/input.jsp" />
```

入力画面 JSP 側では、画面ごとに出し分けたい部分を `forInputPage` / `forConfirmationPage` で囲みます：

```jsp
<%-- 入力・確認画面共通 JSP の差分部分 --%>
<n:forInputPage>
  <n:submit type="submit" value="確認へ" />
</n:forInputPage>

<n:forConfirmationPage>
  <n:submit type="submit" value="登録" />
</n:forConfirmationPage>
```

**注意点**:

- 表示制御の対象は**入力系タグ**のみです。非入力タグには適用されません。
- 以下の2タグは例外で、入力・確認画面の**両方**で出力されます：
  - `plainHidden`タグ：画面遷移の状態受け渡し用
  - `hiddenStore`タグ：セッションストアのデータ受け渡し用
- `ignoreConfirmation` はチェックボックスなど、確認画面でもチェック欄を表示したい場合に使います。

参照: `component/libraries/libraries-tag.json#s3`, `component/libraries/libraries-tag.json#s23`, `component/libraries/libraries-tag-reference.json#s64`, `component/libraries/libraries-tag-reference.json#s65`, `component/libraries/libraries-tag-reference.json#s66`, `component/libraries/libraries-tag-reference.json#s67`