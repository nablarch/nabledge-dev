**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行います。ただしJavaScriptエスケープは提供しないため、script要素内やonclick属性への動的値の埋め込みはプロジェクト側で制限する必要があります。IPA基準では5-(i)・(v)・(viii)・(x)をNablarchがカバーし、残りはプロジェクト対応が必要です。

**根拠**:

**カスタムタグのHTMLエスケープ**

Nablarchのカスタムタグ（`n:write` など）は、出力時に以下のHTMLエスケープを自動で行います：

| 文字 | 変換後 |
|------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

EL式（`${value}`）はHTMLエスケープを行わないため、値の出力にはカスタムタグを使用することが必須です。

**注意**: JavaScriptエスケープは提供していません。`<script>` タグのボディや `onclick` 属性など、JavaScriptを記述する部分には動的な値を埋め込まないこと。やむを得ず埋め込む場合はプロジェクトの責任でエスケープしてください。

**IPAチェックリスト対応範囲**

| 項目 | Nablarch対応 |
|------|-------------|
| 5-(i) ウェブページ出力要素のエスケープ | ✅ カスタムタグがサニタイジング |
| 5-(ii) URLをhttp/httpsのみ許可 | ❌ プロジェクト対応 |
| 5-(iii) `<script>` 要素内の動的生成禁止 | ❌ プロジェクト対応 |
| 5-(iv) スタイルシートの外部取り込み制御 | ❌ プロジェクト対応 |
| 5-(v) 入力値のチェック | ✅ 入力値チェック機能 |
| 5-(vi) HTMLパーサでスクリプト除外 | ❌ プロジェクト対応（OSSのHTMLパーサ使用を推奨） |
| 5-(vii) スクリプト文字列の排除 | ❌ プロジェクト対応 |
| 5-(viii) Content-Type + charset指定 | ✅ HTTP文字エンコード制御ハンドラ |
| 5-(ix) HttpOnly属性・TRACEメソッド無効化 | ❌ プロジェクト対応 |
| 5-(x) XSS対策レスポンスヘッダ | ✅ セキュアハンドラ（`X-XSS-Protection` 等） |

**セキュアハンドラの設定例**

セキュアハンドラにより `X-Frame-Options`、`X-XSS-Protection`、`X-Content-Type-Options` などのヘッダがデフォルトで付与されます：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />
    </list>
  </property>
</component>
```

**CSP対応（より強固なXSS対策）**

`ContentSecurityPolicyHeader` とnonce生成を組み合わせることで、より強固なXSS対策が可能です：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <!-- 他のヘッダも含める -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

**エスケープ漏れ防止ツール**

JSP静的解析ツールにより、カスタムタグ以外のタグ使用を検出し、サニタイジング漏れを開発時に検知できます。

**注意点**:
- `rawWriteタグ` や `prettyPrintタグ`（非推奨）はHTMLエスケープを行いません。不特定ユーザが設定できる値をこれらで出力すると、XSS脆弱性の直接の要因となります
- `rawWriteタグ` を使う場合は、OSSのHTMLパーサで入力値を事前にバリデーションしてください

参照: check/security-check/security-check-2.チェックリスト.json:s5, component/libraries/libraries-tag.json:s2, component/libraries/libraries-tag.json:s50, component/libraries/libraries-tag.json:s27, component/handlers/handlers-secure-handler.json:s4, component/handlers/handlers-secure-handler.json:s6, component/handlers/handlers-secure-handler.json:s8, development-tools/toolbox/toolbox-01-JspStaticAnalysis.json:s1