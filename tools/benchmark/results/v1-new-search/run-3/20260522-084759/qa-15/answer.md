必要なセクションが揃いました。回答を生成します。

---

**結論**: NablarchのJSPカスタムタグを使えば、HTML出力に対するサニタイジング（HTMLエスケープ）が自動で行われ、XSSの根本的解決（IPA対策 5-(i)）が可能です。ただしJavaScript部分のエスケープ・URL制限・スクリプト動的生成禁止はカスタムタグではカバーされず、プロジェクト側での対応が必要です。

---

**根拠**:

### カスタムタグによるHTMLエスケープ（対応 ◎）

カスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、JSPでカスタムタグを使って実装している限りエスケープ漏れを防げます。

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>

<%-- カスタムタグを使えば自動でHTMLエスケープされる --%>
<n:write name="form.userName" />
<n:text name="form.userId" />
```

EL式（`${variable}`）を直接JSPで使うとHTMLエスケープされないため、値の出力にはカスタムタグを使うこと。

**重要な制限**: JavaScriptに対するエスケープ処理は提供していないため、`<script>`タグのボディや`onclick`属性など、JavaScript を記述する部分に動的な値（入力データなど）を埋め込まないこと。埋め込む場合はプロジェクト側でエスケープ処理を実装すること。

### JSP静的解析ツール（エスケープ漏れ防止）

NablarchはJSPで使用を許可する構文とタグを規定し、カスタムタグ以外のタグ使用（エスケープ漏れの原因）を検出する静的解析ツールを提供しています。

### セキュアハンドラによる保険的対策（対応 ◎）

`SecureHandler`がデフォルトで以下のセキュリティヘッダを自動設定します：

```
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store
```

さらにContent Security Policy（CSP）にも対応しており、nonceを生成してCSPヘッダに埋め込む設定が可能です：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <!-- ... 他のヘッダ ... -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

### HTTP文字エンコード制御ハンドラ（対応 ◎）

レスポンスの`Content-Type`に文字コード（charset）を設定し、ブラウザのコンテンツスニッフィングを使ったXSSを防ぎます（IPA対策 5-(viii)）。

### Nablarchがカバーしない対策（要プロジェクト対応）

| IPA対策項目 | 内容 | Nablarch対応 |
|---|---|---|
| 5-(ii) | URLを`https://`のみに制限する | × プロジェクト対応必要 |
| 5-(iii) | `<script>`要素の内容を動的生成しない | × プロジェクト対応必要 |
| 5-(iv) | スタイルシートの外部取り込み制限 | × プロジェクト対応必要 |
| 5-(vi) | HTMLテキスト入力時のパーサによる無害化 | × プロジェクト対応必要（OSSのHTMLパーサを使用するなど） |
| 5-(ix) | CookieへのHttpOnly属性付与 | × プロジェクト対応必要 |

---

**注意点**:
- `<n:rawWrite>`タグはHTMLエスケープせずに出力するため、ユーザ入力値に使用してはいけません
- Nablarchカスタムタグはウェブアプリケーション（JSP）向けの機能です。Thymeleafなど他のテンプレートエンジンを使う場合は、そのエンジン側のエスケープ仕様を確認してください
- JSP静的解析ツールを開発プロセスに組み込むことで、カスタムタグ以外の出力タグの使用を検出できます

参照: security-check-2.チェックリスト.json:s21, security-check-2.チェックリスト.json:s22, security-check-2.チェックリスト.json:s23, security-check-2.チェックリスト.json:s24, security-check-2.チェックリスト.json:s25, security-check-2.チェックリスト.json:s26, security-check-2.チェックリスト.json:s28, security-check-2.チェックリスト.json:s30, libraries-tag.json:s2, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8

---