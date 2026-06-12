**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行います。カスタムタグを使った出力に限れば、IPA定義の「根本的解決 5-(i)：全要素へのエスケープ処理」は達成できます。ただし、XSS対策の全項目をNablarchがカバーするわけではなく、対応範囲外の対策はプロジェクト側の実装が必要です。

---

**根拠**:

#### カスタムタグのHTMLエスケープ（対応：〇）

カスタムタグは原則として出力時に全HTMLの属性についてHTMLエスケープを行います。

エスケープの変換内容：

| 元の文字 | 変換後 |
|----------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

**EL式は対象外**：JSPのEL式（`${value}` など）はHTMLエスケープされないため、値を出力する箇所には必ず `<n:write>` などのカスタムタグを使用してください。

#### JavaScriptへのエスケープは提供していない（プロジェクト対応必須）

`<script>` タグのボディや `onclick` 属性など、JavaScriptを記述する部分への動的な値の埋め込みには、Nablarchはエスケープ処理を提供していません。これらの箇所への動的値の埋め込みは避けるか、プロジェクト側でエスケープを実施してください。

#### エスケープなし出力タグに注意（rawWrite・prettyPrint）

以下のカスタムタグはHTMLエスケープを**行いません**。不特定ユーザが設定できる値に使用すると、XSS脆弱性の直接の要因となります：

- `rawWriteタグ`：変数内の文字列をそのまま出力
- `prettyPrintタグ`（非推奨）：装飾系HTMLタグをエスケープせずに出力

#### Nablarchのセキュリティ対応範囲（XSS チェックリスト）

| IPA対策項目 | Nablarch対応 | 対応機能 |
|-------------|--------------|----------|
| 5-(i) 全要素へのエスケープ処理 | **〇 根本的解決** | カスタムタグ |
| 5-(ii) URLをhttp/httpsのみ許可 | **×** | プロジェクト対応 |
| 5-(iii) `<script>` の内容を動的生成しない | **×** | プロジェクト対応 |
| 5-(iv) スタイルシートを任意サイトから取り込まない | **×** | プロジェクト対応 |
| 5-(v) 入力値の内容チェック | **〇 保険的対策** | 入力値のチェック |
| 5-(vi) HTMLパーサによるスクリプト排除 | **×** | プロジェクト対応 |
| 5-(viii) Content-Typeへの文字コード指定 | **〇 根本的解決** | HTTP文字エンコード制御ハンドラ |
| 5-(ix) Cookie の HttpOnly 属性 | **×** | プロジェクト対応 |
| 5-(x) XSS潜在的脆弱性対策の応答ヘッダ | **〇 保険的対策** | セキュアハンドラ |

#### JSP静的解析ツールによるサニタイジング漏れ防止

NablarchはJSPで使用を許可する構文・タグを規定し、カスタムタグ以外のタグ（EL式など）の使用を検出できるJSP静的解析ツールを提供しています。このツールを併用することで、エスケープ漏れをビルド時に検出できます。

#### 保険的対策：セキュアハンドラ

セキュアハンドラを設定することで、以下のセキュリティ関連HTTPヘッダが自動で付与されます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />
    </list>
  </property>
</component>
```

#### Content Security Policy (CSP) 対応

より高度な保険的対策として、CSPヘッダをセキュアハンドラで設定できます。nonce方式を使う場合の例：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <!-- 他のヘッダ設定省略 -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` プレースホルダーはリクエストごとに生成されたnonceに置換されます。この設定が有効な場合、カスタムタグが生成する `<script>` 要素には自動でnonce属性が付与されます。

---

**注意点**:

- EL式（`${value}`）は絶対に使用しないこと。カスタムタグ（`<n:write>`等）で出力すること。
- `rawWriteタグ` は不特定ユーザの入力値に使用しないこと。使用が必要な場合はOSSのHTMLパーサで事前バリデーションを行うこと。
- `prettyPrintタグ` は非推奨。同様の用途には「OSSのHTMLパーサでバリデーション → rawWriteで出力」の手順を採用すること。
- JavaScriptを記述する箇所（`<script>` ボディ、`onclick` 属性等）への動的値の埋め込みは避けること。

---

参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, libraries-tag.json:s27, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, libraries-tag.json:s38, toolbox-01-JspStaticAnalysis.json:s1