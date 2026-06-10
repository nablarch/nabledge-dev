**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、通常の値出力においてXSS（クロスサイトスクリプティング）の根本的解決が可能です。ただし、JavaScriptへのエスケープやURL出力の制御などはカスタムタグの対象外であり、プロジェクト側で対応が必要です。

---

**根拠**:

#### カスタムタグによるHTMLエスケープ（サニタイジング）

カスタムタグは原則として出力時にすべてのHTML属性をHTMLエスケープします。

変換内容:
```
&  →  &amp;
<  →  &lt;
>  →  &gt;
"  →  &#034;
'  →  &#039;
```

値を出力する際は `writeタグ` などのカスタムタグを使えば自動的にエスケープされるため、通常の入力値表示ではXSSを防げます。

#### Nablarchの対応範囲（セキュリティチェックリストより）

| IPA対策項目 | Nablarch対応 | 備考 |
|---|---|---|
| 5-(i) 全出力要素にエスケープを施す | **〇** | カスタムタグがサニタイジングを行う |
| 5-(ii) URLはhttp/httpsのみ許可 | **×** | プロジェクト対応が必要 |
| 5-(iii) `<script>` 要素の内容を動的生成しない | **×** | プロジェクト対応が必要 |
| 5-(iv) スタイルシートを任意サイトから取り込まない | **×** | プロジェクト対応が必要 |
| 5-(v) 入力値チェック | **〇** | 入力値のバリデーション機能で対応 |
| 5-(viii) Content-Typeに文字コード指定 | **〇** | HTTP文字エンコード制御ハンドラが設定 |
| 5-(x) XSS対策レスポンスヘッダを返す | **〇** | セキュアハンドラが対応 |

#### セキュアハンドラによる保険的対策

セキュアハンドラ（`nablarch.fw.web.handler.SecureHandler`）はデフォルトで以下のレスポンスヘッダを設定します：

```
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Cache-Control: no-store
```

これにより、ブラウザのXSS対策機能を有効化できます。

#### CSP（Content Security Policy）対応

セキュアハンドラと `ContentSecurityPolicyHeader`、カスタムタグのCSP対応を組み合わせることで、CSPによるXSS攻撃の検知・軽減が可能です。カスタムタグがJavaScriptを出力する箇所は、nonceを生成してレスポンスヘッダやscript要素に埋め込む形で対応します。

---

**注意点**:

1. **EL式は使わない**: JSPでEL式（`${...}`）を使って値を出力するとHTMLエスケープされません。値の出力には必ずカスタムタグ（`writeタグ`など）を使用してください。

2. **JavaScriptへのエスケープはカバーされない**: `scriptタグのボディ`や`onclick属性`など、JavaScript記述箇所には動的な値を埋め込まないこと。どうしても必要な場合はプロジェクト責任でエスケープ処理を実施してください。

3. **`rawWriteタグ`の使用に注意**: HTMLエスケープなしで出力するため、不特定ユーザが設定できる値に使うとXSS脆弱性の直接の要因になります。

4. **`prettyPrintタグ`は非推奨**: 設定が複雑かつHTMLとして正しいかのチェックが不十分なため非推奨です。HTMLを含む装飾が必要な場合は、OSSのHTMLパーサでバリデーションしてから`rawWriteタグ`で出力するか、Markdownで入力してクライアントサイドで変換する方法を検討してください。

5. **JSP静的解析ツール**: NablarchはJSPの許可タグをチェックする静的解析ツール（`nablarch-testing-XXX.jar`）を提供しています。これを使うことでカスタムタグ以外のタグ使用によるエスケープ漏れを防止できます。

参照: `component/libraries/libraries-tag.json:s2`, `component/libraries/libraries-tag.json:s27`, `component/libraries/libraries-tag.json:s50`, `check/security-check/security-check-2.チェックリスト.json:s5`, `component/handlers/handlers-secure-handler.json:s6`, `development-tools/toolbox/toolbox-01-JspStaticAnalysis.json:s1`