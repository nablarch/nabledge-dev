**結論**: NablarchのJSPカスタムタグは出力時にHTMLエスケープ（サニタイジング）を自動で行うため、カスタムタグを使って値を出力している限りXSS（5-(i)の根本的解決）は対応済みです。ただしカバー範囲は限定的で、URL検証・scriptタグへの動的値埋め込み防止・スタイルシート制限（5-(ii)〜(iv)）はプロジェクト側での対応が必要です。

---

**根拠**:

### カスタムタグが自動サニタイズする範囲

`<n:write>` タグなどNablarchのカスタムタグは、デフォルトで以下のHTMLエスケープ変換を行います。

| 入力 | 変換後 |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

実装例：
```jsp
<!-- リクエストスコープの値をHTMLエスケープして出力 -->
<n:write name="person.personName" />
```

> **注意**: EL式（`${...}`）はHTMLエスケープを行わないため、値の出力にはEL式を使わずカスタムタグを使用すること。

### Nablarchが対応しているXSS対策の範囲

セキュリティチェックリストにおけるNablarchの対応状況：

| 実施項目 | Nablarch対応 | 担当 |
|---|---|---|
| 5-(i): 出力全要素にエスケープ処理 | ✅ | カスタムタグ |
| 5-(ii): URLをhttp/httpsのみ許可 | ❌ | プロジェクト |
| 5-(iii): `<script>` の動的生成禁止 | ❌ | プロジェクト |
| 5-(iv): 任意サイトからのスタイルシート禁止 | ❌ | プロジェクト |
| 5-(v): 入力値チェック | ✅ | 入力値チェック機能 |
| 5-(viii): Content-Typeにcharset指定 | ✅ | HTTP文字エンコード制御ハンドラ |
| 5-(x): ブラウザXSS対策有効化ヘッダ返却 | ✅ | セキュアハンドラ |

### JavaScriptへのエスケープは対象外

カスタムタグはHTML属性のエスケープは行いますが、**JavaScriptに対するエスケープ処理は提供していません**。`<script>` タグのボディや `onclick` 属性など、JavaScript を記述する部分には動的な値を埋め込まないこと。やむを得ず埋め込む場合はプロジェクトの責任でエスケープすること。

### エスケープなし出力タグの取り扱い

以下のタグはHTMLエスケープを行わないため、使用時は十分な考慮が必要です。

- **`rawWriteタグ`**: 変数の内容をそのまま出力。不特定ユーザが任意に設定できる値に使用するとXSS脆弱性の直接要因になります。
- **`prettyPrintタグ`**: 一部HTMLタグをエスケープせずに出力（非推奨）。

### Content Security Policy (CSP) による追加対策

セキュアハンドラとカスタムタグを組み合わせてCSPを実現できます。セキュアハンドラでnonceを生成し、カスタムタグが生成するscript要素のnonce属性に自動で設定します。

```xml
<!-- セキュアハンドラのデフォルトヘッダ設定例 -->
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

---

**注意点**:
- JSP静的解析ツール（`toolbox-01-JspStaticAnalysis`）を使用することで、カスタムタグ以外のタグ使用によるエスケープ漏れを検出できます。
- `rawWriteタグ` と `prettyPrintタグ` の使用は、管理者がメンテナンス情報を設定するような限定的なケースに限定し、不特定ユーザが入力できる値には絶対に使用しないこと。

参照:
- 2.チェックリスト
  .claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md
  クロスサイト・スクリプティング
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  HTMLエスケープ漏れを防げる
  HTMLエスケープせずに値を出力する
  値を出力する
  HTMLエスケープと改行、半角スペース変換
  Content Security Policy(CSP)に対応する
- セキュアハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md
  デフォルトで適用されるヘッダの値を変更したい
  Content Security Policy(CSP)に対応する
- タグリファレンス
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md
  writeタグ
  rawWriteタグ