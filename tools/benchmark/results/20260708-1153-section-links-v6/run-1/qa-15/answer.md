**結論**: Nablarchのカスタムタグ（JSP）を使えば、HTMLエスケープ（サニタイジング）が自動的に行われ、XSSの根本的解決が可能です。ただし、対応できる範囲には限界があり、JavaScript部分やHTML入力許可のケース、Cookie HttpOnly属性などはプロジェクト側の対応が必要です。

---

**根拠**:

**カスタムタグによるサニタイジング**

NablarchのカスタムタグはデフォルトですべてのHTML属性に対してHTMLエスケープを行います。変換内容は以下の通りです。

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

これにより、IPA 5-(i)「ウェブページに出力する全ての要素に対して、エスケープ処理を施す」の根本的解決が可能です。

ただし、**JavaScriptのエスケープ処理は提供していません**。scriptタグのボディやonclick属性などJavaScriptを記述する部分には動的な値を埋め込まないでください。埋め込む場合はプロジェクトの責任でエスケープ処理を実施する必要があります。

**EL式の使用禁止**

EL式はHTMLエスケープを行わないため、値を出力する場合は `write` タグなどのカスタムタグを使用してください。

**JSP静的解析ツール**

NablarchはJSPで使用を許可する構文とタグを規定し、カスタムタグ以外の使用（エスケープ漏れ）を検出するJSP静的解析ツールを提供しています。このツールを組み合わせることで、エスケープ漏れの防止が強化できます。

**セキュアハンドラによる追加対策**

セキュアハンドラ（`SecureHandler`）を使用すると、XSS対策に有効なセキュリティ関連レスポンスヘッダが設定されます（5-(x)、保険的対策）。またHTTP文字エンコード制御ハンドラにより、Content-TypeへのcharsetがXSS対策として機能します（5-(viii)）。

さらにセキュアハンドラとカスタムタグを組み合わせることで、**Content Security Policy(CSP)**に対応することも可能です。

**Nablarchで対応できない項目（プロジェクト対応が必要）**

| 対策項目 | 内容 |
|---------|------|
| 5-(ii) | URLを `http://` または `https://` 始まりのみ許可 |
| 5-(iii) | `<script>...</script>` の内容を動的に生成しない |
| 5-(iv) | スタイルシートを任意サイトから取り込まない |
| 5-(vi) | HTMLテキスト入力を許可する場合のスクリプト除去 |
| 5-(vii) | HTMLテキストからスクリプト該当文字列を排除 |
| 5-(ix) | CookieにHttpOnly属性を付加・TRACEメソッド無効化 |

**注意点**:

- `rawWrite` タグを使用するとHTMLエスケープなしで値が出力されます。意図的にHTMLを出力する場合にのみ使用し、ユーザ入力値には使用しないでください。
- HTMLテキストの入力を許可する要件がある場合、NablarchではなくOSSのHTMLパーサや、Markdownで入力・クライアントサイドで変換する方法を検討してください。

---

参照:
- セキュリティチェックリスト
  .claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md
  クロスサイト・スクリプティング
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  HTMLエスケープ漏れを防げる
  HTMLエスケープと改行、半角スペース変換
- セキュアハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md
  デフォルトで適用されるヘッダの値を変更したい
  Content Security Policy(CSP)に対応する