**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を自動実施します。ただし、すべてのXSS対策がカバーされるわけではなく、JavaScript文脈のエスケープなどはプロジェクト側の対応が必要です。

**根拠**:

カスタムタグによるサニタイジング（対応済み）:
Nablarchのカスタムタグは出力時にデフォルトでHTMLエスケープを行います。`&`→`&amp;`、`<`→`&lt;`、`>`→`&gt;`、`"`→`&#034;`、`'`→`&#039;` の5文字が変換されます。これによりIPA「安全なウェブサイトの作り方」の根本的解決 5-(i)「ウェブページに出力する全ての要素に対して、エスケープ処理を施す」への対応が可能です。

セキュアハンドラによる保険的対策（対応済み）:
SecureHandlerはデフォルトで `X-XSS-Protection: 1; mode=block`、`X-Frame-Options: SAMEORIGIN`、`X-Content-Type-Options: nosniff`、`Cache-Control: no-store` を設定します。CSP（Content Security Policy）にも対応しています。

JSP静的解析ツールによるエスケープ漏れ検出（追加対策）:
EL式の直接使用などによるエスケープ漏れをJSP静的解析ツールで検出できます。

**注意点**:
- JavaScriptへのエスケープは非対応（プロジェクト対応必須）。`<script>`ボディやonclick属性などに動的な値を埋め込む場合はプロジェクト側でエスケープ処理を実施すること。
- EL式は使用禁止。値の出力には必ず`<n:write>`などのカスタムタグを使用すること。
- `rawWriteタグ`はエスケープなしで出力するため、ユーザー入力値に使用するとXSS脆弱性の直接要因となります。
- URLを`http://`/`https://`のみ許可する対策、`<script>`要素の内容を動的に生成しない対策、CookieへのHttpOnly属性付与などはNablarch未対応（プロジェクト対応必須）。

参照: check/security-check/security-check-2.チェックリスト.json#s21〜s30, component/libraries/libraries-tag.json#s2, component/handlers/handlers-secure-handler.json#s1〜s6, development-tools/toolbox/toolbox-01-JspStaticAnalysis.json#s1