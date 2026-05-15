**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、カスタムタグを使って実装している限りXSSの根本的解決（IPA基準 5-(i)）に対応できます。ただし、Nablarchが対応できるのはXSS対策全体の一部であり、URL出力・script要素の動的生成・スタイルシート取り込みなどはプロジェクト側での対応が必要です。

**根拠**:

**1. カスタムタグによるサニタイジング（根本的解決 5-(i)）**

NablarchのJakarta Server Pagesカスタムタグ（`nablarch-fw-web-tag`）はデフォルトでHTMLエスケープを行います。JSPでEL式を直接使用すると`<`・`>`・`"`などの特殊文字がエスケープされずXSS脆弱性につながりますが、Nablarchのカスタムタグは値を出力する際に自動的にHTMLエスケープを施すため、カスタムタグを使っている限りエスケープ漏れを防げます。

**2. JSP静的解析ツールによるエスケープ漏れ防止**

Nablarchは「JSPで使用を許可する構文とタグを規定し、許可された構文とタグのみ使用していること」をチェックするJSP静的解析ツール（Jakarta Server Pages静的解析ツール）を提供しています。このツールを使うことで、カスタムタグ以外のタグ（EL式など）を使用したエスケープ漏れを検出・防止できます。

**3. セキュアハンドラによる保険的対策（5-(x)）**

セキュアハンドラ（`nablarch.fw.web.handler.SecureHandler`）はデフォルトで以下のセキュリティ関連レスポンスヘッダを設定します：

- `X-XSS-Protection: 1; mode=block`
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cache-Control: no-store`

`X-XSS-Protection`ヘッダにより、XSS対策を無効にしているブラウザに対してもサーバ側から機能有効化を指示できます（5-(x) 保険的対策）。

また、セキュアハンドラはContent Security Policy（CSP）にも対応しており、`ContentSecurityPolicyHeader`を設定することでXSSを含むコンテンツインジェクション攻撃の影響を軽減できます。

**4. HTTP文字エンコード制御（5-(viii)）**

NablarchはHTTPレスポンスヘッダの`Content-Type`にMIMEタイプと文字コードを設定することで、特定ブラウザで発生し得る「エスケープ回避型XSS」も防ぎます。

**5. Nablarchが対応できないXSS対策項目**

以下の対策はNablarchでは未対応（×）であり、プロジェクト側での対応が必要です：

| 項目 | IPA解説 | Nablarch対応 |
|------|---------|-------------|
| URL出力制限 | `http://`/`https://`のみ許可 | × |
| script要素の動的生成禁止 | `<script>...</script>`の内容を動的生成しない | × |
| スタイルシート取り込み制限 | 任意サイトからのCSS取り込み不可 | × |
| Cookie HttpOnly属性 | HttpOnly属性の付与 | × |
| HTMLテキスト入力許可時の構文解析 | スクリプトを含まない要素のみ抽出 | × |

**注意点**:

1. **JavaScriptへのエスケープは非対応**: カスタムタグはHTMLエスケープを提供しますが、JavaScriptエスケープは提供していません。`<script>`タグのボディや`onclick`属性など、JavaScriptを記述する部分に動的な値を埋め込む場合は、プロジェクトの責任でエスケープ処理を実装する必要があります。

2. **`rawWriteタグ`/`prettyPrintタグ`使用時は要注意**: HTMLエスケープせずに値を出力する`rawWriteタグ`は、不特定ユーザが任意に設定できる値を出力する場合、XSS脆弱性の直接の要因となります。`prettyPrintタグ`も`<script>`タグや`onclick`属性を使用可能に設定した場合はXSS脆弱性の要因となるため使用不可。両タグの利用には十分な考慮が必要です（`prettyPrintタグ`は現在非推奨）。

3. **HTMLテキスト入力を許可する場合**: OSSのHTMLパーサを使ったバリデーションや、MarkdownとJavaScriptライブラリの組み合わせによるクライアントサイド変換をプロジェクトで実装する必要があります。

参照: `check/security-check/security-check-2.チェックリスト.json#s21`, `check/security-check/security-check-2.チェックリスト.json#s28`, `check/security-check/security-check-2.チェックリスト.json#s30`, `component/libraries/libraries-tag.json#s2`, `component/libraries/libraries-tag.json#s27`, `component/handlers/handlers-secure-handler.json#s1`, `component/handlers/handlers-secure-handler.json#s6`, `development-tools/toolbox/toolbox-01-JspStaticAnalysis.json#s1`