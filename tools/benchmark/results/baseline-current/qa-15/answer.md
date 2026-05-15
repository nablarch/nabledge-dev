**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、カスタムタグを使って出力している限り、XSSの根本的解決（IPA 5-(i)）が可能です。ただし、JavaScriptへのエスケープは提供されておらず、一部の対策はプロジェクト側での実装が必要です。

**根拠**:

Nablarchが対応している対策（〇）

| IPA分類 | 対策内容 | Nablarchの対応機能 |
|---------|---------|------------------|
| 5-(i) 根本的解決 | 全出力要素にエスケープ処理を施す | カスタムタグ（デフォルトでHTMLエスケープ） |
| 5-(viii) 根本的解決 | Content-Typeに文字コード(charset)を指定する | HTTP文字エンコード制御ハンドラ |
| 5-(v) 保険的対策 | 入力値の内容チェックを行う | 入力値のチェック（バリデーション） |
| 5-(x) 保険的対策 | XSS対策ブラウザ機能を有効にするレスポンスヘッダを返す | セキュアハンドラ（X-XSS-Protectionなど） |

カスタムタグのエスケープ動作:
JSPでEL式を使うとHTMLエスケープされませんが、Nablarchのカスタムタグはデフォルトでエスケープするため、使用している限りエスケープ漏れを防げます。さらに、JSP静的解析ツール（nablarch-testing-XXX.jar）を使うことで、カスタムタグ以外のタグが使われていないかをチェックし、エスケープ漏れを機械的に検出できます。

**注意点**:

Nablarchが未対応の対策（×）— プロジェクト対応必要

| IPA分類 | 対策内容 | 対応方針 |
|---------|---------|---------|
| 5-(ii) | URLをhttp://またはhttps://のみ許可 | プロジェクトで実装 |
| 5-(iii) | <script>内容を動的に生成しない | プロジェクトで実装 |
| 5-(vi) | HTMLテキスト入力時にHTMLパーサで解析・無害化 | OSSのHTMLパーサまたはMarkdown変換ライブラリを使用 |

カスタムタグのJavaScriptエスケープ非対応（重要）:
onclick属性やscriptタグのボディなど、JavaScriptを記述する部分にはカスタムタグのエスケープが効きません。動的な値を埋め込む場合はプロジェクトの責任でJavaScriptエスケープを実施してください。

参照: check/security-check/security-check-2.チェックリスト.json#s21 / component/libraries/libraries-tag.json#s2 / check/security-check/security-check-2.チェックリスト.json#s28 / check/security-check/security-check-2.チェックリスト.json#s30 / development-tools/toolbox/toolbox-01-JspStaticAnalysis.json#s1