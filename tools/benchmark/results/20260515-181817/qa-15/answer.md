**結論**: Nablarchのカスタムタグ（`n:write`等）はデフォルトでHTMLエスケープを行うため、カスタムタグを使って実装している限りXSSの根本的な原因となるエスケープ漏れを防げます。ただし、JavaScriptへの動的値の埋め込みなど一部はプロジェクト対応が必要です。

**根拠**:

カスタムタグによるHTMLエスケープ（自動サニタイジング）

`n:write`等のカスタムタグは出力時に以下の変換を自動適用します：
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&#034;`
- `'` → `&#039;`

これはIPAのXSS対策「5-(i) ウェブページに出力する全ての要素に対してエスケープ処理を施す」の根本的解決に対応しています。

EL式（`${...}`）はHTMLエスケープを行わないため、値の出力には必ずカスタムタグを使用する必要があります。

エスケープせずに出力するタグ:
- `n:prettyPrint`タグ — 特定HTMLタグをエスケープせず出力。`<script>`や`onclick`を許可するとXSS脆弱性に直結するため現在は非推奨
- `n:rawWrite`タグ — 文字列をそのまま出力。不特定ユーザーが設定可能な変数に使用すると脆弱性の要因になる

JavaScriptへのエスケープはNablarchカスタムタグではカバーしていません。`<script>`ボディや`onclick`属性等に動的値を埋め込まないことが原則です。

セキュアハンドラ（`SecureHandler`）はデフォルトで以下のヘッダを設定：
- `X-XSS-Protection: 1; mode=block`
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cache-Control: no-store`

Content Security Policy（CSP）にも対応しており、nonceを使ったスクリプトインジェクション対策が可能です。

JSP静的解析ツールにより、EL式の直接出力などエスケープ漏れを静的にチェックできます。

**注意点**:

以下はプロジェクト側での対応が必要（Nablarchでは対応していません）：
- URLを出力する際に`http://`/`https://`のみ許可（5-(ii)）
- `<script>`要素の内容を動的生成しない（5-(iii)）
- スタイルシートを任意サイトから取り込まない（5-(iv)）
- HTMLテキスト入力時のスクリプト排除（5-(vi)/(vii)）- OSSのHTMLパーサ等を活用
- Cookie の HttpOnly 属性・TRACEメソッド無効化（5-(ix)）

参照: knowledge/component/libraries/libraries-tag.json#s2, knowledge/component/libraries/libraries-tag.json#s27, knowledge/component/handlers/handlers-secure-handler.json#s1, knowledge/check/security-check/security-check-2.チェックリスト.json#s21, knowledge/development-tools/toolbox/toolbox-01-JspStaticAnalysis.json#s1