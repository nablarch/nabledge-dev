必要なセクションの内容が揃いました。Step 4のセクションをまとめます。

**read_sections**: 
- `check/security-check/security-check-2.チェックリスト.json:s5`
- `component/libraries/libraries-tag.json:s2`
- `component/libraries/libraries-tag.json:s26`
- `component/libraries/libraries-tag.json:s27`
- `component/libraries/libraries-tag.json:s50`
- `component/handlers/handlers-secure-handler.json:s4`
- `component/handlers/handlers-secure-handler.json:s6`
- `component/handlers/handlers-secure-handler.json:s7`
- `component/handlers/handlers-secure-handler.json:s8`

Step 5: 回答を生成します。

---

**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、カスタムタグを一貫して使う限りXSS（5-(i)）の根本的解決が可能です。ただし、Nablarchが対応できない項目（JavaScript内への動的値の埋め込み、URLスキーム検証など）についてはプロジェクト側での対応が必要です。

**根拠**:

**1. カスタムタグによるHTMLエスケープ（対応済）**

カスタムタグは原則として全てのHTML出力でHTMLエスケープを行います。変換内容は以下のとおりです。

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

値の出力には `<n:write>` タグを使用します。

```jsp
<!-- HTMLエスケープされて出力される -->
<n:write name="person.personName" />
```

EL式（`${}`）はHTMLエスケープを行わないため、値の出力にEL式を使わないことが重要です。

**2. Nablarchが対応できる範囲と対応できない範囲**

| IPA対策項目 | Nablarchでの対応 |
|---|---|
| 5-(i) 出力要素のエスケープ | ✅ カスタムタグが自動でサニタイジング |
| 5-(v) 入力値チェック | ✅ 入力値チェック機能 |
| 5-(viii) Content-Typeに文字コード指定 | ✅ HTTP文字エンコード制御ハンドラ、セキュアハンドラ |
| 5-(x) ブラウザのXSS対策機能を有効化するレスポンスヘッダ | ✅ セキュアハンドラ（`XssProtectionHeader`等） |
| 5-(ii) URLスキーム検証（http/httpsのみ許可） | ❌ プロジェクト対応が必要 |
| 5-(iii) `<script>` 要素の内容を動的生成しない | ❌ プロジェクト対応が必要 |
| 5-(iv) スタイルシートの任意サイトからの取り込み禁止 | ❌ プロジェクト対応が必要 |
| 5-(ix) CookieへのHttpOnly属性付与 | ❌ プロジェクト対応が必要 |

**3. JavaScript記述箇所への注意（カスタムタグで非対応）**

JavaScriptに対するエスケープ処理は提供されていません。`<script>` タグのボディや `onclick` 属性などJavaScriptを記述する箇所には、動的な値（入力データ等）を埋め込まないことが必要です。埋め込む場合はプロジェクトの責任でエスケープ処理を実施します。

**4. セキュアハンドラによるレスポンスヘッダ設定**

セキュアハンドラ（`SecureHandler`）は `X-Frame-Options`・`X-XSS-Protection`・`X-Content-Type-Options` などのセキュリティ関連ヘッダをレスポンスに自動付与します。さらにCSP対応が必要な場合は `ContentSecurityPolicyHeader` を追加設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
      <!-- 他のヘッダ設定 -->
    </list>
  </property>
</component>
```

**5. `rawWrite`・`prettyPrint` タグの使用注意**

HTMLエスケープせずに出力する `rawWriteタグ` や `prettyPrintタグ`（非推奨）を使う場合、出力内容が不特定ユーザーにより設定可能な場合はXSSの直接要因になります。これらの使用には十分な考慮が必要です。

**6. JSP静的解析ツールによる補助**

NablarchはJSPで許可するタグと構文をチェックするJSP静的解析ツールを提供しており、カスタムタグ以外のタグによるエスケープ漏れを検出できます。

**注意点**:
- EL式（`${value}`）は絶対に使わない。値の出力は常に `<n:write>` 等のカスタムタグを使用する
- JavaScript記述箇所（`onclick`属性、`<script>`ボディ）には動的値を埋め込まない
- `rawWriteタグ` は不特定ユーザーが書き込める値には使用しない
- 5-(ii)～(iv)・5-(ix) はNablarchでカバーされないため、プロジェクト独自の対策が必要

参照: `check/security-check/security-check-2.チェックリスト.json:s5`, `component/libraries/libraries-tag.json:s2`, `component/libraries/libraries-tag.json:s50`, `component/libraries/libraries-tag.json:s27`, `component/handlers/handlers-secure-handler.json:s4`, `component/handlers/handlers-secure-handler.json:s6`

---

Step 6: verify実行します。

主なNablarch固有の主張を確認します：
1. 「カスタムタグはサニタイジングを行う」→ s5, s2で明確に裏付けられている ✅
2. 「EL式はHTMLエスケープしない」→ s50で明確に記載 ✅
3. 「JavaScriptに対するエスケープ処理は提供していない」→ s2で明確に記載 ✅
4. 「XssProtectionHeader」→ s4のコード例に記載 ✅
5. 「ContentSecurityPolicyHeader」、「generateCspNonce」→ s8で明確に記載 ✅
6. 「$cspNonceSource$」プレースホルダー → s8のコード例で確認 ✅
7. 「rawWriteタグはXSSの直接要因となる」→ s27で明確に記載 ✅
8. 5-(ii)〜(iv)が未対応 → s5で「×」と明記 ✅

verify_result = PASS

---

### 回答

**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープ（サニタイジング）を行うため、カスタムタグを一貫して使う限りXSSの根本的解決（IPA対策項目 5-(i)）が可能です。ただしJavaScript内への動的値埋め込みやURLスキーム検証などはNablarchの範囲外であり、プロジェクト側での対応が必要です。

**根拠**:

### Nablarchが対応できる範囲と対応できない範囲

| IPA対策項目 | Nablarchでの対応 |
|---|---|
| 5-(i) 出力要素のエスケープ | ✅ カスタムタグが自動サニタイジング |
| 5-(v) 入力値チェック | ✅ 入力値チェック機能 |
| 5-(viii) Content-Typeに文字コード指定 | ✅ HTTP文字エンコード制御ハンドラ + セキュアハンドラ |
| 5-(x) ブラウザのXSS対策機能を有効化するレスポンスヘッダ | ✅ セキュアハンドラ（`XssProtectionHeader` 等） |
| 5-(ii) URLスキーム検証（http/https のみ許可） | ❌ プロジェクト対応が必要 |
| 5-(iii) `<script>` 要素の内容を動的生成しない | ❌ プロジェクト対応が必要 |
| 5-(iv) 任意サイトからのスタイルシート取り込み禁止 | ❌ プロジェクト対応が必要 |
| 5-(ix) CookieへのHttpOnly属性付与 | ❌ プロジェクト対応が必要 |

### カスタムタグによるHTMLエスケープ

カスタムタグは原則として全てのHTML出力でHTMLエスケープを行います。

| 文字 | 変換後 |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

値の出力には `<n:write>` タグを使用します。

```jsp
<!-- HTMLエスケープされて出力される -->
<n:write name="person.personName" />
```

### セキュアハンドラによるレスポンスヘッダ

セキュアハンドラ（`SecureHandler`）は `X-XSS-Protection` などのセキュリティ関連ヘッダを自動付与します。CSP対応には `ContentSecurityPolicyHeader` を追加します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
      <!-- 他のヘッダ設定 -->
    </list>
  </property>
</component>
```

**注意点**:
- **EL式（`${value}`）は使わない** — EL式はHTMLエスケープを行わないため、値の出力は常に `<n:write>` 等のカスタムタグを使用する
- **JavaScript記述箇所には動的値を埋め込まない** — JavaScriptに対するエスケープ処理はカスタムタグでは提供されていない。`onclick` 属性や `<script>` ボディへの動的値の埋め込みはプロジェクトの責任でエスケープ処理を実施すること
- **`rawWriteタグ` の使用注意** — 不特定ユーザーが設定できる値を `rawWriteタグ` で出力するとXSSの直接要因となる
- **JSP静的解析ツールの活用** — Nablarchが提供するJSP静的解析ツールを使うことで、カスタムタグ以外のタグによるエスケープ漏れを検出できる

参照: `check/security-check/security-check-2.チェックリスト.json:s5`, `component/libraries/libraries-tag.json:s2`, `component/libraries/libraries-tag.json:s50`, `component/libraries/libraries-tag.json:s27`, `component/handlers/handlers-secure-handler.json:s4`, `component/handlers/handlers-secure-handler.json:s6`, `component/handlers/handlers-secure-handler.json:s8`

---