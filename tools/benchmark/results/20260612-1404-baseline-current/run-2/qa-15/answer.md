**結論**: Nablarchのカスタムタグを使えばHTML出力はデフォルトでHTMLエスケープ（サニタイジング）される。これによりIPA XSS対策の根本的解決項目「全要素のエスケープ処理（5-(i)）」は自動的にカバーできる。ただし、JavaScriptへのエスケープ・URL許可制御・`<script>`要素内への動的値埋め込み防止などはNablarchでは対応しておらず、プロジェクト側の対応が必要。

---

**根拠**

**1. カスタムタグによるHTMLエスケープ（自動サニタイジング）**

Nablarchのカスタムタグは、原則としてすべての出力属性に対してHTMLエスケープを自動適用する。変換内容は以下のとおり：

| 文字 | 変換後 |
|------|--------|
| `&`  | `&amp;` |
| `<`  | `&lt;` |
| `>`  | `&gt;` |
| `"`  | `&#034;` |
| `'`  | `&#039;` |

JSPでカスタムタグを使って出力している限り、HTMLエスケープ漏れを防げる。

**2. IPA XSS対策チェックリストにおけるNablarchの対応範囲**

| チェック項目 | Nablarchの対応 | 備考 |
|---|---|---|
| 5-(i) 全要素のエスケープ処理 | ✅ カスタムタグで自動対応 | |
| 5-(ii) URLスキーム検証 (`http://`/`https://`のみ許可) | ❌ 未対応 | プロジェクト対応必要 |
| 5-(iii) `<script>...</script>`内へ動的値を生成しない | ❌ 未対応 | プロジェクト対応必要 |
| 5-(iv) 外部スタイルシート取り込み禁止 | ❌ 未対応 | プロジェクト対応必要 |
| 5-(v) 入力値のチェック | ✅ 入力値チェック機能で対応 | |
| 5-(viii) `Content-Type`に文字コード指定 | ✅ HTTP文字エンコード制御ハンドラ | |
| 5-(x) ブラウザのXSS防御ヘッダ返却 | ✅ セキュアハンドラで対応 | `X-XSS-Protection: 1; mode=block` |

**3. セキュアハンドラによるヘッダ設定**

セキュアハンドラ（`SecureHandler`）はデフォルトで `X-XSS-Protection` ヘッダを返す。また、Content Security Policy（CSP）ヘッダの付与にも対応している：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <!-- CSPを追加する場合 -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

**4. JSP静的解析ツールによるサニタイジング漏れ検出**

NablarchはJSPで使用を許可する構文とタグを規定し、それ以外のタグ（EL式など）の使用を検出するJSP静的解析ツールを提供している。このツールを使うことで、カスタムタグ以外による出力でのエスケープ漏れを自動検出できる。

---

**注意点**

- **EL式は使用しないこと**: EL式（`${...}`）はHTMLエスケープを行わないため、値の出力には必ず `<n:write>` などのカスタムタグを使用する
- **`<script>`内・`onclick`属性への動的値埋め込み禁止**: NablarchはJavaScriptへのエスケープ処理を提供していない。scriptタグのボディやonclick属性には動的な値を埋め込まないこと。埋め込む場合はプロジェクトの責任でエスケープ処理を実施する
- **`rawWrite`タグ・`prettyPrint`タグはXSSリスクあり**: これらはHTMLエスケープせずに出力するため、不特定ユーザが設定できる値に使用するとXSS脆弱性の直接要因となる。`prettyPrint`タグは非推奨。使用する場合は`<script>`タグやonclick属性を使用可能タグ・属性に含めないこと

参照: component/libraries/libraries-tag.json:s2, component/libraries/libraries-tag.json:s27, component/libraries/libraries-tag.json:s50, check/security-check/security-check-2.チェックリスト.json:s5, component/handlers/handlers-secure-handler.json:s4, component/handlers/handlers-secure-handler.json:s6, component/handlers/handlers-secure-handler.json:s7, development-tools/toolbox/toolbox-01-JspStaticAnalysis.json:s1