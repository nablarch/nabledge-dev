**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープを行うため、「ウェブページへの全要素エスケープ処理」（IPA 5-(i)）は根本的に解決できます。ただし、JavaScript部分へのエスケープや一部の対策項目はカバーされておらず、プロジェクト側での対応が必要です。

---

**根拠**

**カスタムタグによるHTMLエスケープ**

カスタムタグは出力時にHTMLの全属性をエスケープします。

| 文字 | 変換後 |
|------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

値の出力には `writeタグ` などのカスタムタグを使用してください。**EL式（`${...}`）はHTMLエスケープを行わないため、値の出力に使用してはいけません。**

**Nablarchで対応できる範囲（IPA XSSチェックリスト）**

| IPA項目 | 性質 | 対応状況 | Nablarchの機能 |
|---------|------|---------|----------------|
| 5-(i) ウェブページへのエスケープ処理 | 根本的解決 | ○ | カスタムタグ |
| 5-(ii) URLスキーム検証 | 根本的解決 | **×** | プロジェクト対応 |
| 5-(iii) `<script>` 要素の内容を動的生成しない | 根本的解決 | **×** | プロジェクト対応 |
| 5-(iv) スタイルシート外部取り込み制限 | 根本的解決 | **×** | プロジェクト対応 |
| 5-(v) 入力値チェック | 保険的対策 | ○ | 入力値チェック |
| 5-(vi)/(vii) HTML入力のサニタイジング | 根本的解決 | **×** | OSSのHTMLパーサを使用して対応（後述） |
| 5-(viii) Content-Type charset指定 | 根本的解決 | ○ | HTTP文字エンコード制御ハンドラ |
| 5-(ix) Cookie HttpOnly属性 | 保険的対策 | **×** | プロジェクト対応 |
| 5-(x) セキュリティヘッダ返却 | 保険的対策 | ○ | セキュアハンドラ |

**セキュアハンドラによる保険的対策**

`X-XSS-Protection` などのセキュリティ関連ヘッダをレスポンスに設定できます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader">
        <property name="option" value="DENY" />
      </component>
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />
    </list>
  </property>
</component>
```

また、セキュアハンドラと `ContentSecurityPolicyHeader` を組み合わせることで、Content Security Policy（CSP）によるXSS対策をさらに強化できます。

**HTMLを許可する入力がある場合（5-(vi)/(vii) 対応）**

rawWriteタグやprettyPrintタグを使ってユーザー入力のHTMLをそのまま出力するとXSS脆弱性の直接要因になります。prettyPrintタグは非推奨です。HTMLを許可する場合は以下の方法で対応してください。

1. OSSのHTMLパーサを使用して入力値をパースし、不正なHTMLタグが含まれていないかをバリデーションする
2. バリデーション済みの値を `rawWriteタグ` で出力する

または、簡易的な装飾であれば利用者にMarkdownで入力してもらい、OSSのJavaScriptライブラリでMarkdown→HTML変換する方法もあります。

---

**注意点**

- **EL式（`${...}`）は絶対に使用しない**: HTMLエスケープされないため、`writeタグ` などのカスタムタグで出力すること
- **JavaScriptへのエスケープ処理はNablarch未提供**: `scriptタグ` のボディや `onclick` 属性など、JavaScriptを記述する部分に動的な値を埋め込んではいけません。どうしても必要な場合はプロジェクトの責任でエスケープ処理を実装してください
- **rawWriteタグ使用時の注意**: 不特定ユーザーが設定できる値を出力する場合は脆弱性の直接要因になるため、必ず事前にHTMLパーサでバリデーションすること
- **JSP静的解析ツールの活用**: `nablarch-testing-XXX.jar` に含まれるツールを使用すると、EL式やカスタムタグ以外の使用によるサニタイジング漏れを静的に検出できます

参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, libraries-tag.json:s27, toolbox-01-JspStaticAnalysis.json:s1, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6