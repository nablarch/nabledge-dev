**結論**: Nablarchのカスタムタグを使えば出力値に対するHTMLエスケープが自動的に行われるため、XSSの根本的解決策（5-(i)）はカバーできます。ただし対応できる範囲に明確な制限があり、URLチェック・scriptタグへの動的値埋め込み禁止・Cookie HttpOnly設定などはプロジェクト側の実装が必要です。

---

**根拠**:

#### Nablarchが対応している項目

| IPA項目 | 内容 | 対応機能 |
|---------|------|---------|
| 5-(i) | 出力値のエスケープ処理（根本的解決） | カスタムタグ |
| 5-(v) | 入力値チェック（保険的対策） | 入力値のチェック機能 |
| 5-(viii) | Content-TypeへのcharSet指定（根本的解決） | HTTP文字エンコード制御ハンドラ、セキュアハンドラ |
| 5-(x) | XSS機能有効化レスポンスヘッダの返却（保険的対策） | セキュアハンドラ |

#### カスタムタグのHTMLエスケープ

カスタムタグはデフォルトで以下の変換を行い、HTMLエスケープ漏れを防ぎます。

```
&  →  &amp;
<  →  &lt;
>  →  &gt;
"  →  &#034;
'  →  &#039;
```

> **重要**: EL式を使って値を出力すると**HTMLエスケープされません**。値の出力には必ず `<n:write>` などのカスタムタグを使用してください。

#### Nablarchが対応していない項目（プロジェクト側で対応が必要）

| IPA項目 | 内容 |
|---------|------|
| 5-(ii) | URLを `http://`/`https://` のみに制限 |
| 5-(iii) | `<script>` 要素の内容を動的生成しない |
| 5-(iv) | スタイルシートの任意サイトからの読み込み禁止 |
| 5-(vi) | HTMLテキストのパース・スクリプト除外 |
| 5-(vii) | HTMLテキストからのスクリプト文字列排除 |
| 5-(ix) | CookieへのHttpOnly属性付与、TRACEメソッド無効化 |

#### セキュアハンドラによる追加対策

セキュアハンドラを使うと `X-XSS-Protection: 1; mode=block` などのセキュリティヘッダが自動付与されます。さらにContent Security Policy (CSP)も設定可能です。

固定ポリシーの例:
```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
      <!-- 他のヘッダも設定 -->
    </list>
  </property>
</component>
```

nonce方式CSPを使う場合は `generateCspNonce` を `true` にすると、カスタムタグが生成するscript要素にnonceが自動設定されます。

#### JSP静的解析ツールによるサニタイジング漏れ検出

Nablarchが提供するJSP静的解析ツール（`nablarch-testing-XXX.jar` 同梱）を使うと、許可されていないタグ・構文の使用を検出し、カスタムタグ以外によるエスケープ漏れを防止できます。

---

**注意点**:

- **JavaScriptエスケープは非提供**: `<script>` タグのボディや `onclick` 属性などJavaScriptを記述する部分には動的な値を埋め込まないこと。埋め込む場合はプロジェクト側でエスケープを実施してください。
- **rawWrite/prettyPrintタグ**: これらはHTMLエスケープを行わないため、不特定ユーザーが設定できる値に対して使用するとXSS脆弱性の直接要因になります。`rawWrite` は特に慎重に扱い、`prettyPrint` は非推奨です。HTMLを動的に出力する場合はOSSのHTMLパーサでバリデーションしてから `rawWrite` を使う方法を検討してください。

参照: `check/security-check/security-check-2.チェックリスト.json:s5`, `component/libraries/libraries-tag.json:s2`, `component/libraries/libraries-tag.json:s50`, `component/libraries/libraries-tag.json:s27`, `component/handlers/handlers-secure-handler.json:s6`, `component/handlers/handlers-secure-handler.json:s7`, `component/handlers/handlers-secure-handler.json:s8`, `development-tools/toolbox/toolbox-01-JspStaticAnalysis.json:s1`

---