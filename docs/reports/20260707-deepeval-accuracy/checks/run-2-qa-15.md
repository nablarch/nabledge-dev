# qa-15 — run-2

## 質問

クロスサイト・スクリプティング（XSS）の対策はNablarchでどこまで対応できるか？カスタムタグを使えばサニタイジングされるのか？

## 回答

**結論**

Nablarchのカスタムタグは出力時に自動でHTMLエスケープ（サニタイジング）を行うため、カスタムタグを一貫して使用する限りXSSの根本的解決策「全要素エスケープ（IPA 5-(i)）」に対応できます。ただしJavaScriptエスケープはNablarchが提供しておらず、URLスキーム制限・script動的生成禁止・HttpOnly属性などはプロジェクトでの対応が必要です。

**根拠**

IPA XSS対策チェックリスト（全10項目）に対するNablarchの対応状況：

| IPA項目 | 実施項目 | Nablarch対応 |
|---|---|---|
| 5-(i) | 全要素HTMLエスケープ | **○ カスタムタグ** |
| 5-(ii) | URL出力をhttp/httpsのみ許可 | × プロジェクト対応 |
| 5-(iii) | script要素の内容を動的生成しない | × プロジェクト対応 |
| 5-(iv) | スタイルシートを外部サイトから取込不可 | × プロジェクト対応 |
| 5-(v) | 入力値の内容チェック | **○ 入力バリデーション** |
| 5-(vi) | HTMLパーサで入力HTMLを処理 | × OSSのHTMLパーサ等で対応 |
| 5-(vii) | 入力HTMLからスクリプト文字列を排除 | × プロジェクト対応 |
| 5-(viii) | Content-Typeにcharset指定 | **○ HTTP文字エンコード制御ハンドラ** |
| 5-(ix) | CookieにHttpOnly属性 | × プロジェクト対応 |
| 5-(x) | XSS軽減のセキュリティヘッダ返却 | **○ SecureHandler** |

カスタムタグのHTMLエスケープ変換内容：`&`→`&amp;`、`<`→`&lt;`、`>`→`&gt;`、`"`→`&#034;`、`'`→`&#039;`

SecureHandlerがデフォルトで設定するXSS関連ヘッダ：`X-XSS-Protection: 1; mode=block`、`X-Frame-Options: SAMEORIGIN`、`X-Content-Type-Options: nosniff`

また、CSP（Content Security Policy）対応も可能です。SecureHandlerでnonceを生成し、カスタムタグがformタグ生成のJavaScriptやscript要素にnonce属性を自動付与することで実現します。

**注意点**

1. **EL式は使わない**：EL式（`${...}`）はHTMLエスケープされません。値の出力には必ずカスタムタグ（`<n:write>`等）を使用してください。
2. **JavaScriptエスケープはプロジェクト対応**：`<script>`ボディや`onclick`属性など、JavaScriptを記述する部分への動的値埋め込みはNablarchでエスケープされません。プロジェクトで明示的にエスケープ処理を実装してください。
3. **JSP静的解析ツールの活用**：Nablarchが提供するJSP静的解析ツールを使うと、カスタムタグ以外のタグ使用（エスケープ漏れの原因）を自動検出できます。
4. **HTMLを直接入力させる場合**：ユーザーがHTMLを入力できる機能ではNablarchでは対応できないため、OSSのHTMLパーサでバリデーション、またはMarkdown変換での代替を検討してください。

**参照**

- [XSSチェックリスト（IPA対応表）](check/security-check/security-check-2.チェックリスト.json#クロスサイトスクリプティング)
- [カスタムタグ：HTMLエスケープ漏れを防げる](component/libraries/libraries-tag.json#htmlエスケープ漏れを防げる)
- [カスタムタグ：HTMLエスケープと改行、半角スペース変換](component/libraries/libraries-tag.json#htmlエスケープと改行半角スペース変換)
- [セキュアハンドラ：デフォルトヘッダ設定変更](component/handlers/handlers-secure-handler.json#デフォルトで適用されるヘッダの値を変更したい)
- [セキュアハンドラ：CSP対応](component/handlers/handlers-secure-handler.json#content-security-policycspに対応する)

## 参照ナレッジ

（なし）

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Expected Output states a single core fact: 'NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能' (Nablarch custom tags can fundamentally solve XSS through sanitization). The Actual Output clearly covers this fact in its conclusion section, explicitly stating that custom tags perform automatic HTML escaping (sanitizing) and can address the fundamental XSS solution '全要素エスケープ（IPA 5-(i)）'. The Actual Output not only contains this fact but elaborates on it extensively with supporting details. The single expected fact is fully present and accurately represented. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the input, directly addressing XSS countermeasures in Nablarch and whether sanitizing is handled through custom tags. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能」は回答の結論「カスタムタグを一貫して使用する限りXSSの根本的解決策『全要素エスケープ（IPA 5-(i)）』に対応できます」に明確に含まれている |
| answer_relevancy | OK | 回答は「XSSの対策はNablarchでどこまで対応できるか」「カスタムタグを使えばサニタイジングされるのか」という質問の両方に直接答えており、IPA XSSチェックリスト10項目に対するNablarchの対応可否を網羅的に示している。的外れな内容は含まれていない。 |
| faithfulness | OK | カスタムタグのHTMLエスケープ機能・変換内容・EL式の非エスケープ・JavaScriptエスケープ未提供・SecureHandlerのデフォルトヘッダ・CSP対応の各記述が、libraries-tag.mdおよびhandlers-secure-handler.mdの記述と一致しており、矛盾する内容は確認されない。 |

### 参照事実（expected_facts）

- NablarchのカスタムタグはサニタイジングによりXSSの根本的解決が可能
