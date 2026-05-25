Step 5-7: 回答を生成し、検証します。

---

**結論**: Nablarchのカスタムタグは原則としてHTMLエスケープによるXSS対策を提供しており、IPA推奨の「全出力要素へのエスケープ」（根本的解決）に対応しています。ただし、JavaScriptエスケープは提供されておらず、HTMLテキスト入力許可・URL出力などの一部対策はプロジェクト側での対応が必要です。

---

**根拠**:

### カスタムタグのHTMLエスケープ

カスタムタグはデフォルトで以下のHTMLエスケープを行います：

| 入力文字 | 出力 |
|---------|------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

> **注意**: EL式（`${...}`）はHTMLエスケープを行いません。値の出力には必ず `writeタグ` などのカスタムタグを使用してください。

### エスケープされない例外ケース

**JavaScriptエスケープは非提供**。scriptタグのボディやonclick属性など、JavaScriptを記述する箇所に動的な値を埋め込まないことが必須です。埋め込む場合はプロジェクト側でエスケープ処理を実施してください。

**`rawWriteタグ`**: エスケープなしで変数内容をそのまま出力します。不特定のユーザが変数内容を設定できる場合、XSS脆弱性の直接の要因となるため十分な考慮が必要です。

**`prettyPrintタグ`**: 装飾系HTMLタグをエスケープせずに出力しますが、**非推奨**です。HTMLテキストを出力したい場合は「OSSのHTMLパーサでバリデーション → rawWriteで出力」か「Markdownで入力してクライアントサイドでHTML変換」の方式を採用してください。

### Nablarchが対応できない部分（プロジェクト対応が必要）

| 対策項目 | 状況 | 対応方法 |
|---------|------|---------|
| URLのhttp/httpsスキーム制限 | × | プロジェクトで実装 |
| HTMLテキスト入力を許可する場合の構文解析・スクリプト排除 | × | OSSのHTMLパーサまたはMarkdown方式 |
| `<script>`タグの動的生成禁止 | × | プロジェクトルールで禁止 |

### Nablarchの追加対策（保険的対策）

**セキュアハンドラ**: ブラウザのXSS保護機能を有効にするレスポンスヘッダを返します（`X-XSS-Protection`等）。

**HTTP文字エンコード制御ハンドラ**: Content-TypeにMIME Type・文字コード（charset）を設定し、特定ブラウザでのエスケープ回避型XSSを防止します。

**CSP（Content Security Policy）対応**: `ContentSecurityPolicyHeader`とカスタムタグのCSP対応を組み合わせることで、コンテンツインジェクション攻撃の検知・軽減が可能です。

### JSP静的解析ツール

許可するJSP構文・タグのみを使用していることをチェックするツール（`nablarch-testing`に同梱）。これにより、カスタムタグ以外の構文・タグ（EL式等）を使ったサニタイジング漏れを検出できます。

---

**注意点**:
- EL式を使って値を出力するとXSSになります。`${value}` ではなく `<n:write value="${value}" />` を使ってください。
- `rawWriteタグ`はシステム管理者がメンテナンス情報を設定するような画面の特定領域のみに限定して使用してください。

---

参照: `security-check-2.チェックリスト.json:s21`、`security-check-2.チェックリスト.json:s26`、`security-check-2.チェックリスト.json:s28`、`security-check-2.チェックリスト.json:s22`、`security-check-2.チェックリスト.json:s30`、`libraries-tag.json:s2`、`libraries-tag.json:s27`、`libraries-tag.json:s50`、`handlers-secure-handler.json:s6`、`toolbox-01-JspStaticAnalysis.json:s1`

---