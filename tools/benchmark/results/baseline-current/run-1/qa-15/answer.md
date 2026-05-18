**結論**: NablarchのJSPカスタムタグ（`<n:write>` 等）を使用している限り、HTMLエスケープ（サニタイジング）は自動で行われ、XSSの根本的解決（IPA 5-(i)）が可能です。ただし、JavaScriptコンテキストへの動的値埋め込みはカスタムタグではカバーされず、プロジェクト側の責任での対処が必要です。

**根拠**:

**1. カスタムタグはデフォルトでHTMLエスケープ（サニタイジング）する**

`<n:write>` などのカスタムタグは出力時に以下の変換を自動適用します：
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&#034;`
- `'` → `&#039;`

確認画面等では改行→`<br />`、半角スペース→`&nbsp;` の変換も追加で行われます。

**2. EL式はHTMLエスケープしない（使用禁止）**

JSPでEL式（`${...}`）を使って値を直接出力するとHTMLエスケープが行われません。値の出力には必ずカスタムタグを使用してください。

**3. セキュリティチェックリストにおけるNablarchの対応範囲**

IPA XSS対策項目に対するNablarchの対応状況：
- 5-(i) 全要素にエスケープ処理: カスタムタグ → 〇
- 5-(ii) URLスキーム制限: × (プロジェクト対応)
- 5-(iii) script要素の動的生成禁止: × (プロジェクト対応)
- 5-(v) 入力値チェック: 入力値チェック機能 → 〇
- 5-(viii) Content-Type文字コード指定: HTTP文字エンコード制御ハンドラ → 〇
- 5-(x) XSS対策ブラウザ機能有効化: セキュアハンドラ → 〇

**4. セキュアハンドラによる保険的対策**

`SecureHandler` はデフォルトで `X-XSS-Protection: 1; mode=block`、`X-Frame-Options: SAMEORIGIN` 等のレスポンスヘッダを設定します。`ContentSecurityPolicyHeader` を使用するとCSPヘッダによるXSSインジェクション攻撃の検知・軽減も設定できます。

**5. HTMLテキスト入力を許可する場合**

`<n:rawWrite>` はエスケープなしで出力するため、不特定ユーザーが設定できる値に使用するとXSS脆弱性の直接要因になります。この場合はプロジェクト側でOSSのHTMLパーサによるサニタイズ処理を実装する必要があります。

**注意点**:

1. **JavaScriptコンテキストはカバー外**: `<script>` タグのボディや `onclick` 属性など、JavaScript記述箇所への動的値埋め込みはカスタムタグが対応しないため、プロジェクトの責任で実施が必要です。
2. **EL式で直接出力しない**: EL式（`${変数}`）をJSP上で直接出力に使うとXSSリスクになります。
3. **JSP静的解析ツール**: `JspStaticAnalysis` でカスタムタグ以外のタグ使用によるエスケープ漏れを防止できます。
4. **IPA 5-(ii)〜(iv)はプロジェクト対応**: URLスキームのチェック、`<script>`の動的生成禁止、外部スタイルシート制限はNablarchがカバーしておらず、プロジェクト側での対応が必要です。

参照: `check/security-check/security-check-2.チェックリスト.json#s21`, `component/libraries/libraries-tag.json#s2`, `component/libraries/libraries-tag.json#s27`, `component/libraries/libraries-tag.json#s50`, `component/handlers/handlers-secure-handler.json#s4`