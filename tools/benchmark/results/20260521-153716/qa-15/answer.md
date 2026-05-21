必要なセクションが揃いました。回答を生成します。

---

**結論**: NablarchのJSPカスタムタグを使えば、出力時のHTMLエスケープ（サニタイジング）が自動適用され、XSSの根本的解決（IPA対策5-(i)）に対応できる。ただし、Nablarchがカバーするのは一部の対策に限られ、JavaScriptコンテキストへの動的値埋め込みや、URLの検証、`<script>`要素の動的生成防止などはプロジェクト側の対応が必要。

**根拠**:

### カスタムタグによるHTMLエスケープ（根本的解決 5-(i)）

カスタムタグはデフォルトで以下の変換を行います：

| 文字 | エスケープ後 |
|------|-------------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

値の出力には `<n:write>` タグを使用します：

```jsp
<!-- name属性を指定してオブジェクトのpersonNameプロパティにアクセスする。 -->
<n:write name="person.personName" />
```

エスケープなし出力が必要な場合は `rawWriteタグ` がありますが、ユーザーが任意に設定できる内容を出力する場合はXSS脆弱性の直接の要因となるため、使用には十分な考慮が必要です。

### JSP静的解析ツールによるエスケープ漏れ検出

JSPで使用を許可する構文とタグを規定し、許可したものだけを使用していることをチェックするツールを提供しています。カスタムタグ以外のタグ（EL式など）によるエスケープ漏れを検出できます。

> **注意**: EL式はHTMLエスケープ処理を行わないため、EL式を使って値を直接出力しないこと。

### 文字コード設定（根本的解決 5-(viii)）

HTTP文字エンコード制御ハンドラにより、HTTPレスポンスヘッダの `Content-Type` にMIME TypeとcharsetがNablarchにより自動設定されます。特定のブラウザで発生し得るエスケープ回避XSSを防げます。

### セキュアハンドラによる保険的対策（5-(x)）

セキュアハンドラにより、XSS脆弱性対策に関するブラウザ機能を有効化するレスポンスヘッダが自動付与されます（`X-Frame-Options: SAMEORIGIN` など）。

またCSP（Content Security Policy）対応には `ContentSecurityPolicyHeader` を使用できます：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

### Nablarchがカバーしない対策（プロジェクト対応が必要）

| IPA対策番号 | 内容 | Nablarch対応 |
|------------|------|-------------|
| 5-(ii) | URLを出力する際、`http://`や`https://`で始まるURLのみ許可 | × |
| 5-(iii) | `<script>...</script>`要素の内容を動的に生成しない | × |
| 5-(iv) | スタイルシートを任意サイトから取り込めないようにする | × |
| 5-(ix) | CookieにHttpOnly属性を加え、TRACEメソッドを無効化 | × |

**注意点**:
- **JavaScriptへのエスケープはカスタムタグでは提供していない**。`script`タグのボディや`onclick`属性など、JavaScriptを記述する部分には動的な値を埋め込まないこと。埋め込む場合はプロジェクト責任でエスケープ処理を実施すること
- HTMLテキストの入力を許可する場合（自由入力でHTMLタグを含む）は、OSSのHTMLパーサを使ったバリデーションや、Markdown→HTML変換などで個別対応が必要

参照: security-check-2.チェックリスト.json:s21, s22, s23, s24, s25, s26, s28, s30 / libraries-tag.json:s2, s27, s50 / handlers-secure-handler.json:s4, s6, s7 / toolbox-01-JspStaticAnalysis.json:s1

---