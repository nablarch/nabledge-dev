**結論**: NablarchのカスタムタグはHTMLエスケープ（サニタイジング）を自動で行うため、XSS対策の根本的解決（IPA基準 5-(i)）が可能です。ただし、JavaScriptエスケープや一部のURL出力・スクリプト動的生成については Nablarch がカバーしないため、プロジェクトで個別対応が必要です。

---

**根拠**:

**カスタムタグが自動サニタイジングする範囲**

カスタムタグ（`n:write` 等）は出力時にデフォルトで以下のHTMLエスケープを行います（`libraries-tag.json:s50`）:

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

これにより、フォーム入力値を画面出力する際のXSSは防止できます。

**カスタムタグがカバーしない範囲**

- **JavaScriptエスケープは提供していません**。`<script>` タグのボディや `onclick` 属性など、JavaScript を記述する箇所に動的な値を埋め込む場合は、プロジェクトの責任でエスケープ処理を実装してください。
- **`rawWriteタグ`・`prettyPrintタグ`**: エスケープせずに出力します。`rawWrite` タグで不特定ユーザが設定できる値を出力した場合、XSS脆弱性の直接の原因になります。
- **EL式（`${...}`）**: HTMLエスケープが行われないため、値出力には `n:write` などのカスタムタグを使用してください。

**Nablarchの対応状況まとめ（IPA対策番号別）**

| IPA対策 | 内容 | Nablarch対応 |
|---------|------|-------------|
| 5-(i) | 出力値のエスケープ処理 | ○ カスタムタグ |
| 5-(ii) | URLを `http://` / `https://` のみ許可 | × プロジェクト対応 |
| 5-(iii) | `<script>` 要素を動的生成しない | × プロジェクト対応 |
| 5-(iv) | 外部スタイルシートの取り込み制限 | × プロジェクト対応 |
| 5-(v) | 入力値チェック（保険的対策） | ○ Bean Validation 等 |
| 5-(viii) | Content-Type に文字コード指定 | ○ HTTP文字エンコード制御ハンドラ |
| 5-(x) | XSS対策ブラウザ機能有効化ヘッダ | ○ セキュアハンドラ |

**追加: JSP静的解析ツール**

NablarchはJSPで使用を許可する構文・タグを規定し、カスタムタグ以外のタグ使用によるエスケープ漏れを検出できる「JSP静的解析ツール」を提供しています（`toolbox-01-JspStaticAnalysis.json:s1`）。

**追加: Content Security Policy (CSP) 対応**

セキュアハンドラと `ContentSecurityPolicyHeader` を組み合わせ、nonceを生成してレスポンスヘッダや `<script>` 要素に埋め込むことで、CSPによる多層防御が可能です（`handlers-secure-handler.json:s6`）。

---

**注意点**:
- EL式を使った値出力は避け、必ず `n:write` 等のカスタムタグを使用してください。
- JavaScript内への動的値の埋め込みはNablarchではエスケープされないため、設計で排除するか、プロジェクト側でエスケープを実装してください。
- HTMLテキスト入力を許可する機能では Nablarch はサポートなし（OSSのHTMLパーサ活用を検討）。

参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, libraries-tag.json:s27, libraries-tag.json:s38, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6, toolbox-01-JspStaticAnalysis.json:s1