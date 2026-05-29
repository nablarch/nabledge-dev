Step 5〜7: 回答を生成し、verify します。

**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープを行うため、カスタムタグを使って値を出力している限りXSS（根本的解決5-(i)）に対応できます。ただし、JavaScriptへのエスケープは提供しないため、scriptタグのボディやonclick属性への動的埋め込みはNablarchの対象外であり、プロジェクト側での対応が必要です。

---

**結論**: カスタムタグを正しく使えば大部分のXSSを防げるが、カバー範囲には明確な限界がある。

**根拠**:

**カスタムタグがHTMLエスケープする内容**

カスタムタグは出力時に以下の5文字をHTMLエスケープします（`libraries-tag.json:s50`）。

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

これにより、**IPA「安全なウェブサイトの作り方」の5-(i)「全要素にエスケープ処理を施す」** が根本的解決として対応済みとなります（`security-check-2.チェックリスト.json:s5`）。

---

**Nablarchがカバーする項目（〇）とカバーしない項目（×）**

| IPA対策番号 | 内容 | 対応 | 手段 |
|-------------|------|------|------|
| 5-(i) | 全要素へのエスケープ処理 | 〇 | カスタムタグ |
| 5-(v) | 入力値チェック | 〇 | 入力値バリデーション機能 |
| 5-(viii) | Content-Typeに文字コード指定 | 〇 | HTTP文字エンコード制御ハンドラ + セキュアハンドラ |
| 5-(x) | ブラウザのXSS対策機能を有効にするレスポンスヘッダ | 〇 | セキュアハンドラ（`XssProtectionHeader`等） |
| 5-(ii) | URL出力時にhttp/httpsのみ許可 | × | プロジェクト対応 |
| 5-(iii) | `<script>`要素の内容を動的生成しない | × | プロジェクト対応 |
| 5-(iv) | 外部スタイルシートの取り込み制限 | × | プロジェクト対応 |
| 5-(vi) | HTMLパーサでスクリプト除去 | × | OSSのHTMLパーサを使用（プロジェクト対応） |
| 5-(ix) | CookieにHttpOnly属性 | × | プロジェクト対応 |

---

**注意が必要なケース**

**1. EL式を直接使用した場合（エスケープされない）**

```jsp
<!-- 危険: HTMLエスケープされない -->
<td>${user.name}</td>

<!-- 安全: カスタムタグ(writeタグ)を使う -->
<n:write name="user.name" />
```

EL式はHTMLエスケープされないため、カスタムタグの`writeタグ`等を使う必要があります（`libraries-tag.json:s50`）。

**2. JavaScript部分への動的値の埋め込み（Nablarch非対応）**

```jsp
<!-- 危険: JavaScriptへのエスケープは提供しない -->
<script>
  var name = "${user.name}";  // XSS脆弱性
</script>
```

scriptタグのボディやonclick属性など、JavaScript部分へのエスケープ処理はNablarchは提供しません（`libraries-tag.json:s2`）。プロジェクトの責任でエスケープ処理を実施する必要があります。

**3. rawWriteタグ・prettyPrintタグ使用時**

`rawWriteタグ`はエスケープなしで値を出力するため、不特定ユーザーが設定できる値を出力するとXSS脆弱性の直接要因になります（`libraries-tag.json:s27`）。

---

**保険的対策: セキュアハンドラとCSP**

セキュアハンドラはデフォルトでXSS対策関連のセキュリティヘッダを付与します（`handlers-secure-handler.json:s4`）。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <!-- ... -->
    </list>
  </property>
</component>
```

さらに追加的なXSS防御として、Content Security Policy（CSP）も対応しています。`ContentSecurityPolicyHeader`をSecureHandlerに設定することで`Content-Security-Policy`ヘッダを付与できます（`handlers-secure-handler.json:s7`）。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'" />
</component>
```

---

**JSP静的解析ツールによるサニタイジング漏れ検出**

Nablarchが提供するJSP静的解析ツールを使うと、カスタムタグ以外のタグ（EL式直接使用など）によるエスケープ漏れをコンパイル前に検出できます（`toolbox-01-JspStaticAnalysis.json:s1`）。例えば、JavaScript中でEL式を使った`var id = ${user.id}`のような記述も指摘対象になります（`toolbox-01-JspStaticAnalysis.json:s3`）。

---

**注意点**:
- カスタムタグを**使っていても**、EL式をそのまま使うとHTMLエスケープされません。値出力は常に`writeタグ`等のカスタムタグで行ってください。
- `rawWriteタグ`はシステム管理者がメンテナンス情報を設定するような限定用途向けです。ユーザー入力を直接出力しないでください。
- `prettyPrint`タグは非推奨です。HTML出力が必要な場合はOSSのHTMLパーサでバリデーションした上で`rawWriteタグ`で出力するか、MarkdownからHTMLへのクライアントサイド変換を検討してください。

参照: `security-check-2.チェックリスト.json:s5`, `libraries-tag.json:s2`, `libraries-tag.json:s50`, `libraries-tag.json:s27`, `handlers-secure-handler.json:s4`, `handlers-secure-handler.json:s7`, `toolbox-01-JspStaticAnalysis.json:s1`, `toolbox-01-JspStaticAnalysis.json:s3`

---