**結論**: NablarchのJSPカスタムタグを使えばHTML出力に対するエスケープ（サニタイジング）は自動で行われ、XSSの根本的解決（IPA 5-(i)）に対応できます。ただし対応範囲は限定的で、URL検証・`<script>` 動的生成禁止・スタイルシート外部参照禁止などはプロジェクト側の対応が必要です。

**根拠**:

### カスタムタグによるエスケープ（根本的解決 ✅）

NablarchのJSPカスタムタグは**デフォルトでHTMLエスケープ（サニタイジング）**を行います。`<`、`>`、`"` 等の文字が自動でエスケープされるため、カスタムタグを使って実装している限りエスケープ漏れを防ぐことができます。

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<!-- 入力値はカスタムタグが自動でHTMLエスケープして出力する -->
<n:write name="form.userName" />
```

また、JSP静的解析ツールを使用することで、カスタムタグ以外のタグが使われたことによるエスケープ漏れを検出できます。

**注意**: JavaScriptに対するエスケープ処理は提供していません。`<script>` タグのボディや `onclick` 属性などJavaScriptを記述する部分には、動的な値（入力データ等）を埋め込まないこと。これを行う場合はプロジェクト側でエスケープ処理を実施する必要があります。

---

### セキュアハンドラによる保険的対策（保険的対策 ✅）

セキュアハンドラ（`SecureHandler`）はデフォルトで以下のセキュリティヘッダをレスポンスに設定します。

```
X-XSS-Protection: 1; mode=block
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store
```

これはIPA 5-(x)「XSS脆弱性対策として有効なブラウザの機能を有効にするレスポンスヘッダ」に対応します。

---

### HTTP文字エンコード制御ハンドラ（根本的解決 ✅）

HTTPレスポンスのContent-TypeヘッダにMIME Typeと文字コードを自動設定します（IPA 5-(viii)）。

---

### Content Security Policy（CSP）対応 ✅

セキュアハンドラの `ContentSecurityPolicyHeader` とカスタムタグのCSP対応機能を組み合わせることで、CSPヘッダの設定・nonceの自動埋め込みが可能です。

---

### Nablarchで対応できない項目（プロジェクト対応が必要）

| IPA項目 | 内容 | 対応状況 |
|--------|------|---------|
| 5-(ii) | URLを `http://` / `https://` のみ許可 | ❌ プロジェクト対応 |
| 5-(iii) | `<script>` 要素の内容を動的生成しない | ❌ プロジェクト対応 |
| 5-(iv) | スタイルシートを任意サイトから取り込まない | ❌ プロジェクト対応 |
| 5-(vi) | HTMLテキスト入力許可時のパース＆フィルタリング | ❌ OSSのHTMLパーサ等で対応 |
| 5-(ix) | CookieにHttpOnly属性を付与 | ❌ プロジェクト対応 |

HTMLテキストの入力を許可する場合の対策例：
- OSSのHTMLパーサを使って使用不可タグを含む入力をバリデーション
- Markdownで入力させてクライアントサイドでHTMLに変換する

**注意点**:
- カスタムタグのJavaScript部分（`onclick`、`<script>` 内）には動的な値を埋め込まないこと
- `n:rawWrite` タグはHTMLエスケープを**しない**出力タグのため、ユーザ入力値には使用しないこと

参照: `security-check-2.チェックリスト.json:s21`, `security-check-2.チェックリスト.json:s22`, `security-check-2.チェックリスト.json:s23`, `security-check-2.チェックリスト.json:s24`, `security-check-2.チェックリスト.json:s25`, `security-check-2.チェックリスト.json:s26`, `security-check-2.チェックリスト.json:s28`, `security-check-2.チェックリスト.json:s30`, `libraries-tag.json:s2`, `handlers-secure-handler.json:s4`, `handlers-secure-handler.json:s6`