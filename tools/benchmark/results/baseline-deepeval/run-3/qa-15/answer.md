これで必要な情報が揃いました。回答を生成します。

---

**結論**: Nablarchのカスタムタグ（`n:write`、`n:text` 等）はHTML要素・属性値のHTMLエスケープを自動で行うため、カスタムタグを使って値を出力する限りXSSの根本的対策（IPA 5-(i)）は可能。ただし対応範囲は**HTML出力のみ**であり、JavaScriptコンテキストのエスケープは対応外。URLスキーム制限・動的script生成禁止・スタイルシート制限（5-(ii)〜(iv)）はプロジェクト側での対応が必要。

---

**根拠**

### カスタムタグのサニタイジング対応範囲

カスタムタグは、値を出力する際に原則として全HTML属性に対して以下のHTMLエスケープを自動適用します。

| 元の文字 | 変換後 |
|---------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

これにより、カスタムタグを使って実装している限り、HTMLエスケープ漏れを防げます。

```jsp
<%-- EL式は HTMLエスケープしないため NG --%>
${form.value}

<%-- writeタグ等のカスタムタグを使う: HTMLエスケープ自動適用 --%>
<n:write name="form.value" />
```

### Nablarchが対応する範囲（〇）

| 対策項目 | 対応するNablarch機能 |
|---------|-------------------|
| 5-(i) 出力全要素へのエスケープ処理 | **カスタムタグ**（根本的解決） |
| 5-(v) 入力値の内容チェック | 入力値のチェック（保険的対策） |
| 5-(viii) Content-Typeに文字コード指定 | HTTP文字エンコード制御ハンドラ |
| 5-(x) XSS対策有効化レスポンスヘッダ返却 | **セキュアハンドラ**（保険的対策） |

`SecureHandler`（`nablarch.fw.web.handler.SecureHandler`）はデフォルトで以下のセキュリティヘッダを設定します：

```
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store
```

また、`ContentSecurityPolicyHeader`を組み合わせることでCSP（Content Security Policy）にも対応できます。

### Nablarchが対応しない範囲（×）: プロジェクト側での対応が必要

- 5-(ii): URLを出力する際に `http://`・`https://` のみ許可する
- 5-(iii): `<script>...</script>` 要素の内容を動的に生成しない
- 5-(iv): スタイルシートを任意サイトから取り込めないようにする
- 5-(vi)/(vii): HTMLテキスト入力を許可する場合のサニタイジング

### 注意点

**JavaScriptコンテキストはカスタムタグのエスケープ対象外です。**

`<script>` タグのボディや `onclick` 属性など、JavaScriptを記述する部分に動的な値（入力データ等）を埋め込む場合は、プロジェクトの責任でJavaScriptエスケープ処理を実装する必要があります。

また、`rawWrite`タグはHTMLエスケープせずに値をそのまま出力するため、不特定ユーザーが設定できる値に使用するとXSS脆弱性の直接要因になります。使用には十分な考慮が必要です。

JSP静的解析ツール（`jakarta.tags.core`以外の素のJSPタグ使用を検知）を導入することで、カスタムタグ以外によるエスケープ漏れをビルド時に防止できます。

参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, libraries-tag.json:s27, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6

---