**結論**: NablarchのカスタムタグはHTMLエスケープ（サニタイジング）をデフォルトで実施するため、IPA基準の「5-(i) 全要素のエスケープ処理」を満たします。ただし、XSS対策の全項目をカバーするわけではなく、プロジェクトで別途対応が必要な項目もあります。

**根拠**:

**カスタムタグによるHTMLエスケープ（5-(i) 根本的解決）**

Nablarchのカスタムタグはデフォルトで以下の文字をHTMLエスケープします：

| 文字 | 変換後 |
|------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

JSPのEL式（`${}`）はHTMLエスケープを行わないため、値の出力には必ず`write`タグ等のカスタムタグを使用する必要があります。

**Nablarchがカバーするその他のXSS対策**

- **5-(viii)**: HTTP文字エンコード制御ハンドラがContent-TypeヘッダにMIME Type・文字コード（charset）を設定し、特定ブラウザでのXSSを防止
- **5-(x) 保険的対策**: セキュアハンドラがXSS関連のブラウザ機能を有効化するレスポンスヘッダを返す
- **CSP対応**: セキュアハンドラ＋`ContentSecurityPolicyHeader`＋カスタムタグのCSP対応を組み合わせることでContent Security Policyを有効化可能

**JSP静的解析ツール**: カスタムタグ以外のタグ使用（エスケープ漏れ）を検出するツールも提供しています。

**注意点**:

1. **JavaScriptエスケープは非対応**: カスタムタグはHTML属性のエスケープのみを提供します。`script`タグのボディや`onclick`属性など、JavaScriptを記述する箇所への動的な値の埋め込みは**プロジェクト責任**でエスケープが必要です。

2. **5-(ii)〜(iv) はプロジェクト対応が必要**: IPA基準の項目5-(ii)〜(iv)（URL・CSS・JavaScriptのエスケープ等）はNablarchでは未対応のため、各プロジェクトで実装してください。

3. **`rawWrite`タグ・`prettyPrint`タグは要注意**: これらはHTMLエスケープをスキップします。`rawWrite`タグで不特定ユーザが設定できる値を出力するとXSS脆弱性の直接の原因になります。使用は最小限に留め、十分な考慮が必要です。

4. **EL式の直接出力は禁止**: 値の出力に`${変数}`をそのまま使用すると、HTMLエスケープされないため、必ずカスタムタグを使用してください。

参照: `check/security-check/security-check-2.チェックリスト.json#s21`、`component/libraries/libraries-tag.json#s2`、`component/libraries/libraries-tag.json#s50`、`component/libraries/libraries-tag.json#s27`、`component/handlers/handlers-secure-handler.json#s6`、`check/security-check/security-check-2.チェックリスト.json#s28`、`check/security-check/security-check-2.チェックリスト.json#s30`