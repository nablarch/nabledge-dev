# qa-15 — run-3

## 質問

クロスサイト・スクリプティング（XSS）の対策はNablarchでどこまで対応できるか？カスタムタグを使えばサニタイジングされるのか？

## 回答

**結論**: NablarchのカスタムタグはHTMLエスケープ（サニタイジング）を自動で行うため、XSS対策の根本的解決（IPA基準 5-(i)）が可能です。ただし、JavaScriptエスケープや一部のURL出力・スクリプト動的生成については Nablarch がカバーしないため、プロジェクトで個別対応が必要です。

---

**根拠**:

**カスタムタグが自動サニタイジングする範囲**

カスタムタグ（`n:write` 等）は出力時にデフォルトで以下のHTMLエスケープを行います（`libraries-tag.json:s50`）:

```
& → &amp;
< → &lt;
> → &gt;
" → &#034;
' → &#039;
```

これにより、フォーム入力値を画面出力する際のXSSは防止できます。

**カスタムタグがカバーしない範囲**

- **JavaScriptエスケープは提供していません**。`<script>` タグのボディや `onclick` 属性など、JavaScript を記述する箇所に動的な値を埋め込む場合は、プロジェクトの責任でエスケープ処理を実装してください。
- **`rawWriteタグ`・`prettyPrintタグ`**: エスケープせずに出力します。`rawWrite` タグで不特定ユーザが設定できる値を出力した場合、XSS脆弱性の直接の原因になります。
- **EL式（`${...}`）**: HTMLエスケープが行われないため、値出力には `n:write` などのカスタムタグを使用してください。

**Nablarchの対応状況まとめ（IPA対策番号別）**

| IPA対策 | 内容 | Nablarch対応 |
|---------|------|-------------|
| 5-(i) | 出力値のエスケープ処理 | ○ カスタムタグ |
| 5-(ii) | URLを `http://` / `https://` のみ許可 | × プロジェクト対応 |
| 5-(iii) | `<script>` 要素を動的生成しない | × プロジェクト対応 |
| 5-(iv) | 外部スタイルシートの取り込み制限 | × プロジェクト対応 |
| 5-(v) | 入力値チェック（保険的対策） | ○ Bean Validation 等 |
| 5-(viii) | Content-Type に文字コード指定 | ○ HTTP文字エンコード制御ハンドラ |
| 5-(x) | XSS対策ブラウザ機能有効化ヘッダ | ○ セキュアハンドラ |

**追加: JSP静的解析ツール**

NablarchはJSPで使用を許可する構文・タグを規定し、カスタムタグ以外のタグ使用によるエスケープ漏れを検出できる「JSP静的解析ツール」を提供しています（`toolbox-01-JspStaticAnalysis.json:s1`）。

**追加: Content Security Policy (CSP) 対応**

セキュアハンドラと `ContentSecurityPolicyHeader` を組み合わせ、nonceを生成してレスポンスヘッダや `<script>` 要素に埋め込むことで、CSPによる多層防御が可能です（`handlers-secure-handler.json:s6`）。

---

**注意点**:
- EL式を使った値出力は避け、必ず `n:write` 等のカスタムタグを使用してください。
- JavaScript内への動的値の埋め込みはNablarchではエスケープされないため、設計で排除するか、プロジェクト側でエスケープを実装してください。
- HTMLテキスト入力を許可する機能では Nablarch はサポートなし（OSSのHTMLパーサ活用を検討）。

参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, libraries-tag.json:s27, libraries-tag.json:s38, handlers-secure-handler.json:s4, handlers-secure-handler.json:s6, toolbox-01-JspStaticAnalysis.json:s1

## 参照ナレッジ

- [クロスサイト・スクリプティング](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md#クロスサイトスクリプティング) (s5)
- [HTMLエスケープ漏れを防げる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#htmlエスケープ漏れを防げる) (s2)
- [HTMLエスケープと改行、半角スペース変換](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#htmlエスケープと改行半角スペース変換) (s50)
- [HTMLエスケープせずに値を出力する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#htmlエスケープせずに値を出力する) (s27)
- [デフォルトで適用されるヘッダの値を変更したい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#デフォルトで適用されるヘッダの値を変更したい) (s4)
- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#content-security-policycspに対応する) (s6)
- [Content Security Policy(CSP)に対応する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#content-security-policycspに対応する) (s38)
- [概要](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/toolbox/toolbox-01-JspStaticAnalysis.md#概要) (s1)
- [デフォルト以外のレスポンスヘッダを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-secure-handler.md#デフォルト以外のレスポンスヘッダを設定する) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the key fact stated in the Expected Output: that Nablarch's custom tags perform sanitizing (HTMLエスケープ/サニタイジング) to fundamentally resolve XSS (根本的解決). The Actual Output explicitly states this in the conclusion and provides detailed supporting evidence, including the specific escape mappings and references to IPA standard 5-(i). The core claim is thoroughly addressed and confirmed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the input, addressing the question about XSS countermeasures in Nablarch and whether sanitizing is performed when using custom tags. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.94 | NG | The score is 0.94 because the actual output slightly misrepresents the relationship between prettyPrint and rawWrite by grouping them together as both 'outputting without escaping', when the retrieval context describes them separately. While prettyPrint does output decorative HTML tags without escaping, equating its escaping behavior directly with rawWrite is a partial misrepresentation of the source material. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能」は回答冒頭の「NablarchのカスタムタグはHTMLエスケープ（サニタイジング）を自動で行うため、XSS対策の根本的解決（IPA基準 5-(i)）が可能です」に明確に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: security-check-2.チェックリスト.json:s5, libraries-tag.json:s2, libraries-tag.json:s50, ...」という内部JSON参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | prettyPrintとrawWriteを「エスケープせずに出力する」とまとめた点はナレッジ記述（両タグとも「HTMLエスケープせずに値を出力する」セクションに属する）と矛盾しない。XSSリスクの直接原因をrawWriteに帰属させた点もナレッジの「直接の要因となる」と一致しており、全体として矛盾なし |

### 参照事実（expected_facts）

- NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能
