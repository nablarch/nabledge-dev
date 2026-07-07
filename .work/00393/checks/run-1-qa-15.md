# qa-15 — run-1

## 質問

クロスサイト・スクリプティング（XSS）の対策はNablarchでどこまで対応できるか？カスタムタグを使えばサニタイジングされるのか？

## 回答

Step 5: Nablarchの資料に基づいて回答を生成します。

---

## Step 5: 回答生成

収集した情報を基に回答を作成します。

---

## Nablarchのウェブアプリケーションにおけるクロスサイト・スクリプティング（XSS）対策

### Nablarchで対応できる範囲

IPAの「安全なウェブサイトの作り方」のXSS対策チェックリスト（5項目）を基準に整理します。

---

#### ✅ Nablarchが対応済み（カスタムタグ・ハンドラを使えば自動対応）

**5-(i) ウェブページ出力のエスケープ処理（根本的解決）**

Nablarchのカスタムタグは**デフォルトでHTMLエスケープ**を行います。JSPでカスタムタグを使って値を出力している限り、エスケープ漏れを防げます。

エスケープ対象文字:
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&#034;`
- `'` → `&#039;`

> **重要な注意点：** カスタムタグでも**JavaScriptに対するエスケープ処理は提供していません**。`<script>` タグのボディや `onclick` 属性など、JavaScriptを記述する部分には動的な値を埋め込まないでください。どうしても埋め込む場合はプロジェクトの責任でエスケープ処理を実装する必要があります。

また、**EL式（`${...}`）はHTMLエスケープしません**。値の出力には必ず `<n:write>` 等のカスタムタグを使ってください。

**5-(v) 入力値の内容チェック（保険的対策）**

Nablarchの入力値チェック機能で対応できます。

**5-(viii) HTTPレスポンスのContent-TypeにcharsetをHTTPヘッダで指定（根本的解決）**

**HTTP文字エンコード制御ハンドラ**（`HttpCharacterEncodingHandler`）がリクエスト・レスポンスに文字エンコーディングを設定します。デフォルトでUTF-8が設定されます。これにより、特定ブラウザで発生しうる文字コード判定を悪用したXSSを防止できます。

**5-(x) ブラウザのXSS保護機能を有効にするレスポンスヘッダ（保険的対策）**

**セキュアハンドラ**（`SecureHandler`）がデフォルトで以下のセキュリティヘッダを全レスポンスに付与します。

| ヘッダ | デフォルト値 |
|--------|-------------|
| `X-XSS-Protection` | `1; mode=block` |
| `X-Frame-Options` | `SAMEORIGIN` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Cache-Control` | `no-store` |

---

#### ✅ Nablarchが追加的に提供（CSP対応）

**Content Security Policy（CSP）**もセキュアハンドラと `ContentSecurityPolicyHeader` を組み合わせることで設定できます。nonce生成機能（`generateCspNonce` プロパティを `true`）も提供しており、カスタムタグが生成する `<script>` 要素に自動でnonce属性が付与されます。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      ...
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

---

#### ✅ JSP静的解析ツールでエスケープ漏れを防止

JSP静的解析ツール（`JspStaticAnalysis`）を使うと、JSPで使用を許可するタグ・構文を設定ファイルで規定し、カスタムタグ以外のタグ（EL式など）が使われていないかCIで自動チェックできます。これにより、カスタムタグ以外のタグ使用によるエスケープ漏れを組織的に防止できます。

---

#### ❌ プロジェクトで個別対応が必要な項目

以下はNablarchでは対応していないため、プロジェクト側で実装・設計が必要です。

| 項目 | 内容 |
|------|------|
| 5-(ii) | URL出力時にhttp/httpsのみ許可する |
| 5-(iii) | `<script>` 要素の内容を動的に生成しない |
| 5-(iv) | 任意サイトからのスタイルシート取込みを禁止する |
| 5-(vi) | 入力されたHTMLからスクリプトを除去する（OSSのHTMLパーサ等を利用） |
| 5-(vii) | HTMLテキストからスクリプト文字列を排除する |
| 5-(ix) | CookieにHttpOnly属性を付与し、TRACEメソッドを無効化する |
| JavaScript文脈のエスケープ | scriptタグボディ・onclickへの動的値埋め込みをプロジェクトで対処 |

---

### まとめ

Nablarchのカスタムタグを使えば**HTML文脈での出力のサニタイジングは自動的に対応**されます（根本的解決）。ただし、**JavaScript文脈のエスケープはカスタムタグでもカバーされない**ため、`<script>` タグ内や `onclick` 属性に動的な値を埋め込むことは避ける必要があります。セキュアハンドラとHTTP文字エンコード制御ハンドラを組み合わせることで保険的対策も自動化できます。プロジェクトとしては、5-(ii)〜(iv)・5-(ix)・JavaScript文脈の対策を別途実装してください。

---

## Step 6: Verify

セクション内容に基づいて各主張を検証します。

**✅ 確認済み主張:**
1. カスタムタグはデフォルトでHTMLエスケープする → `libraries-tag.json:s2` に明記
2. JavaScriptエスケープはカスタムタグも提供しない → `libraries-tag.json:s2` の Important note
3. EL式はHTMLエスケープしない → `libraries-tag.json:s50` に明記
4. セキュアハンドラのデフォルトヘッダ一覧 → `handlers-secure-handler.json` の content にすべて記載
5. 5-(i)がカスタムタグで根本的解決 → `security-check-2.チェックリスト.json:s5` に「〇」で記載
6. 5-(ii)〜(iv)はプロジェクト対応 → `security-check-2.チェックリスト.json:s5` 解説に明記
7. 5-(viii)はHTTP文字エンコード制御ハンドラで対応 → `security-check-2.チェックリスト.json:s5` に「〇」
8. 5-(x)はセキュアハンドラで対応 → `security-check-2.チェックリスト.json:s5` に「〇」
9. JSP静的解析ツールでサニタイジング漏れ検出 → `toolbox-01-JspStaticAnalysis.json:s1` に明記
10. CSPはセキュアハンドラ + ContentSecurityPolicyHeader + nonceで対応 → `handlers-secure-handler.json:s6,s7,s8`

**Result: PASS** — すべての主張がセクション内容に裏付けられています。

---

## 参照ナレッジ

（なし）

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly states that Nablarch's custom tags perform HTML escaping by default, which constitutes sanitization for fundamental XSS prevention. The section '5-(i) ウェブページ出力のエスケープ処理（根本的解決）' directly addresses the Expected Output's claim that custom tags enable XSS fundamental resolution through sanitization. The summary also confirms 'HTML文脈での出力のサニタイジングは自動的に対応されます（根本的解決）'. The single expected fact is fully covered. |
| answer_relevancy | 0.95 | 0.77 | NG | The score is 0.77 because while the actual output addresses the core XSS question regarding Nablarch's capabilities and custom tag sanitization, it is weighed down by numerous source citation/verification notes and a meta-statement about response validation that are not directly relevant to answering the question. These 11 irrelevant statements dilute the response, preventing a higher score. The score remains at 0.77 because the substantive content does address the XSS and Nablarch custom tag sanitization topic. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能」は回答まとめ「Nablarchのカスタムタグを使えばHTML文脈での出力のサニタイジングは自動的に対応されます（根本的解決）」および5-(i)節「NablarchのカスタムタグはデフォルトでHTMLエスケープを行います」に含まれている |
| answer_relevancy | NG | 回答に「Step 5: Nablarchの資料に基づいて回答を生成します」「Step 6: Verify」などワークフローメタ記述と、`libraries-tag.json:s2`・`security-check-2.チェックリスト.json:s5`などの内部JSON参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | 参照ナレッジが「（なし）」のため知識ファイルとの直接照合は不可。ただし回答内Step 6 Verifyセクションで各主張が具体的なナレッジファイル（libraries-tag.json、handlers-secure-handler.json等）と照合されており、矛盾の証拠なし |

### 参照事実（expected_facts）

- NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能
