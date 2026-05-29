セクション内容から回答を生成します。

---

**結論**: NablarchのJSPカスタムタグを使用することで、出力時のHTMLエスケープ（サニタイジング）によるXSS対策の根本的解決（IPA 5-(i)）が可能です。ただし、URLスキームチェックや `<script>` 要素の動的生成禁止など、いくつかの対策はNablarchの機能対象外であり、プロジェクトでの個別対応が必要です。

**根拠**:

**カスタムタグによるサニタイジング（対応可）**

Nablarchのカスタムタグは原則として出力時に全てのHTML属性をHTMLエスケープします。変換内容は以下の通りです。

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

これにより、カスタムタグを使って実装している限りHTMLエスケープ漏れを防げます（IPAの5-(i) 根本的解決に対応）。

さらに、NablarchはJSPで使用を許可する構文とタグを規定し、許可する構文とタグのみを使用していることをチェックするJSP静的解析ツールを提供しています。このツールを使用することでカスタムタグ以外のタグを使用したことによるエスケープ漏れを防止することが可能です。

**セキュアハンドラによる保険的対策（対応可）**

`SecureHandler`はデフォルトで以下のセキュリティヘッダを設定します。

```
X-XSS-Protection: 1; mode=block
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store
```

これにより、ユーザがXSS対策を無効にしていた場合でもサーバからブラウザの機能を有効にするよう指示することが可能です（IPA 5-(x) 保険的対策に対応）。

**注意点**:

- **EL式の使用禁止**: EL式はHTMLエスケープを行いません。値の出力には `<n:write>` などのカスタムタグを必ず使用してください。
- **JavaScriptエスケープは対象外**: scriptタグのボディやonclick属性などJavaScriptを記述する部分には動的な値を埋め込まないこと。JavaScriptに対するエスケープ処理はカスタムタグでは提供されていないため、プロジェクト責任での対応が必要です。
- **`rawWriteタグ`の危険性**: `<n:rawWrite>` はHTMLエスケープなしで値をそのまま出力します。不特定のユーザによって任意に設定できる値を出力する場合は、XSSの直接要因となります。
- **プロジェクト個別対応が必要な項目（Nablarchは×）**:
  - URLスキームチェック（http://・https://のみ許可）(5-(ii))
  - `<script>` 要素の動的生成禁止 (5-(iii))
  - 外部スタイルシートの取り込み制限 (5-(iv))
  - CookieへのHttpOnly属性付与 (5-(ix))
  - HTMLテキスト入力を許可する場合の構文解析ベースのサニタイズ (5-(vi))

参照: `check/security-check/security-check-2.チェックリスト.json:s5`, `component/libraries/libraries-tag.json:s2`, `component/libraries/libraries-tag.json:s50`, `component/libraries/libraries-tag.json:s27`, `component/handlers/handlers-secure-handler.json`

---