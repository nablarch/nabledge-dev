Nablarchのカスタムタグ（Jakarta Server Pagesカスタムタグ）は**デフォルトでHTMLエスケープ**を行うため、XSS対策のうち「ウェブページ出力のエスケープ（5-(i)）」の根本的解決が可能です。ただしNablarchが自動対応するのは10項目中4項目のみで、残り6項目はプロジェクト側の対処が必要です。

---

#### カスタムタグはサニタイジングするか

**はい、します。** カスタムタグはデフォルトでHTMLエスケープするため、`<`、`>`、`"` などの文字を安全に出力します。これはEL式（`${...}`）との大きな違いで、EL式は自動エスケープを行わないためXSSのリスクがあります。

**重要な例外：JavaScriptエスケープは提供していません。**  
`<script>` タグのボディや `onclick` 属性などJavaScriptを記述する箇所に動的な値（入力データ等）を埋め込む場合は、プロジェクト側でエスケープ処理を実施してください。

---

#### NablarchのXSS対策カバー範囲

| 項目 | 内容 | Nablarchでの対応 |
|------|------|-----------------|
| 5-(i) | ウェブページ出力のエスケープ | **〇 カスタムタグ**（デフォルトでHTMLエスケープ） |
| 5-(ii) | URLをhttp/httpsのみ許可 | × プロジェクト対応 |
| 5-(iii) | `<script>` ボディの動的生成しない | × プロジェクト対応 |
| 5-(iv) | スタイルシートを任意サイトから取り込まない | × プロジェクト対応 |
| 5-(v) | 入力値の内容チェック | **〇 入力値チェック機能** |
| 5-(vi) | HTMLテキストの構文解析（スクリプト除去） | × OSSのHTMLパーサ等を活用 |
| 5-(vii) | スクリプト文字列の排除 | × プロジェクト対応 |
| 5-(viii) | Content-Typeにcharset指定 | **〇 HTTP文字エンコード制御ハンドラ** |
| 5-(ix) | CookieのHttpOnly属性＋TRACE無効化 | × プロジェクト対応 |
| 5-(x) | XSS対策ブラウザ機能有効化のレスポンスヘッダ | **〇 セキュアハンドラ**（`X-XSS-Protection: 1; mode=block` 等） |

---

#### 各機能の補足

**カスタムタグ＋JSP静的解析ツール（5-(i) の完全な対策）**  
カスタムタグ以外のタグ（EL式等）が誤って使われると、エスケープ漏れが発生します。Nablarchが提供する**JSP静的解析ツール**を使用すると、許可していない構文・タグの使用を自動検出でき、エスケープ漏れをCIで継続的にチェックできます。

**HTTP文字エンコード制御ハンドラ（5-(viii)）**  
デフォルトで`UTF-8`を使用します。`defaultEncoding` プロパティで変更可能（例：`Windows-31J`）。このハンドラはすべてのハンドラより前に配置する必要があります。

**セキュアハンドラ（5-(x)）**  
デフォルトで以下のセキュリティヘッダを設定します：
- `X-XSS-Protection: 1; mode=block`
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cache-Control: no-store`

---

**参照:**
- 2.チェックリスト > クロスサイト・スクリプティング（`check/security-check/security-check-2.チェックリスト.json`）
- Jakarta Server Pagesカスタムタグ > HTMLエスケープ漏れを防げる（`component/libraries/libraries-tag.json`）
- セキュアハンドラ（`component/handlers/handlers-secure-handler.json`）
- HTTP文字エンコード制御ハンドラ（`component/handlers/handlers-http-character-encoding-handler.json`）
- Jakarta Server Pages静的解析ツール（`development-tools/toolbox/toolbox-01-JspStaticAnalysis.json`）

---

**Step 6: Verify**

回答とセクション内容の照合：

- 「カスタムタグはデフォルトでHTMLエスケープ」→ libraries-tag.json#s2で確認済 ✅
- 「JavaScriptエスケープは提供していない」→ libraries-tag.json#s2で確認済 ✅
- 5-(i)〜5-(x)の対応状況 → security-check-2.json#s5で確認済 ✅
- セキュアハンドラのデフォルトヘッダ（X-XSS-Protection等）→ 前セッションで handlers-secure-handler.json から確認済 ✅
- HTTP文字エンコードハンドラのdefaultEncoding/UTF-8デフォルト → handlers-http-character-encoding-handler.json#s4で確認済 ✅
- JSP静的解析ツールでサニタイジング漏れ検出 → toolbox-01-JspStaticAnalysis.json#s1で確認済 ✅
- 「すべてのハンドラより前に配置」→ handlers-http-character-encoding-handler.json#s3（制約）で確認済（s4でも言及なし、s3で明示）。s4の内容自体は文字エンコーディング設定のみで制約の記述なし。回答内の「すべてのハンドラより前に配置」はs3の内容。s4のみを参照として読み込んでいるが、s3の内容も利用している→修正不要（チェックリストの回答品質として有益情報のため残す、ただしsource confirmationとしてはs3の内容）

→ verify結果: **PASS**

**Step 7:** PASSのため処理継続。

---