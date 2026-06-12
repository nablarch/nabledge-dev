**結論**: NablarchのカスタムタグはHTMLエスケープ（サニタイジング）を自動で行うため、カスタムタグを使って実装している限りXSS対策（IPA 5-(i)「全出力要素にエスケープ処理」）の根本的解決が可能です。一方で、JavaScriptコンテキストへのエスケープや一部の対策はNablarchではカバーされず、プロジェクト側での対応が必要です。

---

**根拠**

#### カスタムタグで対応できる部分

**① HTMLエスケープの自動適用（5-(i)）— 根本的解決〇**

`n:write` タグ等のカスタムタグは、デフォルトでHTMLエスケープするため、カスタムタグを使って実装している限りエスケープ漏れを防げます。

```jsp
<%-- writeタグ: 自動でHTMLエスケープされる --%>
<n:write name="person.personName" />

<%-- EL式は HTMLエスケープされないため使用しないこと --%>
<%-- ${person.personName} は危険 --%>
```

JSP静的解析ツール（`JspStaticAnalysis`）を併用することで、カスタムタグ以外のタグ使用によるエスケープ漏れを自動検出できます。

**② セキュアハンドラによるレスポンスヘッダ設定（5-(viii)(x)）— 保険的対策〇**

`SecureHandler` をハンドラキューに設定すると、以下のセキュリティヘッダがデフォルトで全レスポンスに付与されます。

```
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store
```

これにより「ブラウザのXSS対策機能を有効にするヘッダを返す（5-(x)）」と「Content-TypeへのMIME Type・文字コード指定（5-(viii)）」が自動対応されます。

**③ Content Security Policy（CSP）への対応**

`SecureHandler` の `generateCspNonce` プロパティを `true` にすると、リクエストごとにnonceを生成してCSPヘッダに埋め込めます。カスタムタグが生成するscript要素には自動でnonce属性が付与されます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <!-- ... 省略 ... -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

---

#### プロジェクトで対応が必要な部分（Nablarchで対応不可）

| IPA対策項目 | 内容 | Nablarchの対応 |
|---|---|---|
| 5-(ii) | URLを `http://` / `https://` 始まりのみ許可 | × プロジェクト対応 |
| 5-(iii) | `<script>` 要素の内容を動的に生成しない | × プロジェクト対応 |
| 5-(iv) | スタイルシートを任意サイトから取り込まない | × プロジェクト対応 |
| 5-(vi)(vii) | HTMLテキスト入力を許可する場合のパース・除去 | × OSSライブラリ利用等でプロジェクト対応 |
| 5-(ix) | CookieにHttpOnly属性 + TRACEメソッド無効化 | × プロジェクト対応 |

---

**注意点**

- **JavaScriptコンテキストへのエスケープは提供していない**: `<script>` タグのボディや `onclick` 属性などJavaScriptを記述する箇所に動的な値を埋め込む場合は、プロジェクト側でエスケープ処理を実施してください。

- **`rawWriteタグ`・`prettyPrintタグ` の使用に注意**: これらのタグはHTMLエスケープせずに出力するため、不特定ユーザが任意に設定できる値を出力するとXSS脆弱性の直接の要因となります。使用には十分な考慮が必要です。

- **EL式は使用しない**: JSP上でEL式（`${...}`）を使って値を出力するとHTMLエスケープされないため、必ずカスタムタグ（`n:write`等）を使用してください。

参照: check/security-check/security-check-2.チェックリスト.json:s5, component/libraries/libraries-tag.json:s2, component/libraries/libraries-tag.json:s27, component/handlers/handlers-secure-handler.json:s4