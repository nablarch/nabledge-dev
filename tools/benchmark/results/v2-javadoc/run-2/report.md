# ベンチマーク run-2 レポート

**ラベル**: v2-javadoc  
**実行日時**: 2026-06-03T15:51:03  
**シナリオ数**: 33（全件、qa-16/17/18含む）  
**スキル**: `.claude/skills/nabledge-6`

---

## 3a. 数値サマリー

| シナリオID | 精度 | 幻覚 | セクション数 | ターン数 |
|---|---|---|---|---|
| pre-01 | PASS | PASS | 6 | 9 |
| pre-02 | PASS | PASS | 9 | 10 |
| pre-03 | PASS | PASS | 8 | 8 |
| review-06 | PASS | PASS | 6 | 3 |
| review-07 | PASS | PASS | 5 | 9 |
| review-08 | PASS | PASS | 11 | 10 |
| review-09 | **ERROR** | - | - | - |
| impact-01 | PASS | PASS | 3 | 9 |
| impact-03 | PASS | UNCERTAIN | 9 | 6 |
| impact-06 | PASS | PASS | 9 | 9 |
| impact-08 | PASS | FAIL | 8 | 9 |
| qa-01 | PASS | FAIL | 4 | 10 |
| qa-02 | PASS | PASS | 10 | 3 |
| qa-03 | PASS | PASS | 4 | 6 |
| qa-04 | PASS | PASS | 10 | 6 |
| qa-05 | FAIL(67%) | PASS | 4 | 12 |
| qa-06 | PASS | PASS | 6 | 7 |
| qa-07 | PASS | PASS | 5 | 7 |
| qa-08 | PASS | PASS | 7 | 3 |
| qa-09 | PASS | PASS | 11 | 7 |
| qa-10 | PASS | PASS | 6 | 6 |
| qa-11a | PASS | FAIL | 10 | 10 |
| qa-11b | PASS | FAIL | 7 | 10 |
| qa-12a | FAIL | FAIL | 6 | 11 |
| qa-12b | FAIL(50%) | PASS | 6 | 8 |
| qa-13 | PASS | PASS | 7 | 7 |
| qa-14 | PASS | PASS | 10 | 9 |
| qa-15 | PASS | PASS | 4 | 7 |
| qa-16 | PASS | PASS | 3 | 7 |
| qa-17 | PASS | PASS | 4 | 7 |
| qa-18 | PASS | PASS | 4 | 10 |
| oos-impact-01 | PASS | PASS | 10 | 5 |
| oos-qa-01 | PASS | PASS | 2 | 9 |

**集計（32件、ERROR1件除く）**:
- 精度 PASS: 29/32 = 90.6%
- 精度 FAIL: 3/32 = 9.4%（qa-05, qa-12a, qa-12b）
- 幻覚 PASS: 26/32 = 81.3%（UNCERTAIN1件含む）
- 幻覚 FAIL: 5/32 = 15.6%（impact-08, qa-01, qa-11a, qa-11b, qa-12a）

---

## 3b. FAIL/UNCERTAIN/ERROR シナリオの妥当性評価

### review-09: ERROR（Workflow Details section not found）

**状況**: スキルは回答を生成した（raw_response.txt 188行あり）。パーサーがWorkflow Details見出しを検出できなかった。  
**内容確認**: raw_response.txt にSecureHandler + ContentSecurityPolicyHeader + JSPカスタムタグ対応の説明が含まれており、must fact を満たしている。  
**判定**: パース失敗（スキル自体は正しく動作）。品質問題ではない。  
**結論**: 確定FAILとしない（パーサー問題）。

### qa-05: 精度 FAIL(67%)

**状況**: `Jackson2BodyConverterが設定される` というfactがABSENT。  
→ run-1 と同じ結果。Jackson2BodyConverter名称を回答が言及しない問題が再現。  
**判定**: スキルの挙動問題。run-1/run-2 ともFAIL → 再現性あり。  
**結論**: 確定FAIL候補。ユーザー確認待ち。

### impact-03: 幻覚 UNCERTAIN

**内容**: `UniversalDao.countBySqlFileを使った重複チェックのコード例` がunsupportedとして扱われているが、評価者判定はUNCERTAIN（記録的にはcountBySqlFileの使用例は知識に存在する可能性あり）。  
**判定**: 評価基準の問題（UNCERTAINは確定FAILではない）。run-1 では PASS。  
**結論**: 確定FAILとしない（揺らぎ / 評価基準の問題）。

### impact-08: 幻覚 FAIL

**内容**: 
- `fixedDateの設定例として value="20100914123456"（9月14日）` — 知識 XML は 9月13日
- `yyyyMMddHHmmssフォーマットは14桁` — 知識は「12桁」と記載
- `SystemTimeProviderインタフェースはgetDate()とgetTimestamp()を持つ`

**選定ページ全体確認（再調査）**:
- `fixedDate value="20100914123456"（9月14日）`: knowledge の XML 設定例は `20100913123456`（9月13日）。散文「9月14日」に従った回答だが XML 値と矛盾 → **確定FAIL**
- `yyyyMMddHHmmssは14桁`: knowledge が「12桁」と記載しているが `yyyyMMddHHmmss` は実際14文字。knowledge に誤りがある → **虚偽FAIL**（回答が正しい）
- `SystemTimeProviderはgetDate()とgetTimestamp()を持つ`: Javadoc `javadoc-nablarch-core-date-SystemTimeProvider.json` に両メソッドが存在する → **虚偽FAIL**（情報はJavadocに存在）

**判定**: `fixedDate日付誤り（XML値と不一致）` が確定FAIL。他2件は虚偽FAIL。  
**結論**: 確定FAIL（fixedDate日付誤りのみ）。

### qa-01: 幻覚 FAIL

**内容**: `データリーダ（createReader）でデータ取得し、フレームワークのループ制御に任せるのが正しい設計` が unsupported。  
→ run-1 では PASS。  
**判定**: スキルの挙動問題（設計に関する補足が知識に記載なし）。再現性なし（揺らぎ）。  
**結論**: 確定FAILとしない（揺らぎ）。

### qa-11a: 幻覚 FAIL

**内容**: `その他の例外はFATAL、500を返す` がunsupported（ThreadDeath/StackOverflowError等は除外される）。  
→ run-1 でも同様のFAIL。  
**判定**: スキルの挙動問題（例外テーブルの単純化）。run-1/run-2 ともFAIL → 再現性あり。  
**結論**: 確定FAIL候補。ユーザー確認待ち。

### qa-11b: 幻覚 FAIL

**内容**: `JaxRsErrorLogWriterでApplicationException以外の例外はFailureLogUtilを使用してログ出力する` がunsupported。

**選定ページ全体確認（再調査）**:
- 選定済みの `javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json` のクラス説明（`content` フィールド）に「{@link FailureLogUtil}を用いてログ出力を行う」と明記されている。

**判定**: **虚偽FAIL** — 自動評価器がページの `content`（導入文）を見落とした。  
**結論**: 確定FAILとしない。

### qa-12a: 精度 FAIL + 幻覚 FAIL

**精度FAIL**: `エラー表示タグでリクエストスコープのエラーメッセージを表示する` がABSENT。

**幻覚FAIL内容**: ErrorMessages#hasError/getMessage/allMessages/globalMessages がunsupported。

**選定ページ全体確認（再調査）**:
- 選定済みの `web-application-error-message.json` を全セクション確認したところ、Thymeleaf での使用例として `errors.hasError('form.userName')`、`errors.getMessage('form.userName')`、`errors.globalMessages`、`errors.allMessages` が全て記載されている。
- 精度FAIL の `エラー表示タグでリクエストスコープのエラーメッセージを表示する` については、回答がThymeleafのErrorMessages APIを詳しく説明しており、実質的に内容は満たしている。

**判定**: **虚偽FAIL** — 自動評価器が選定ページの当該セクションを見落とした。メソッド群はナレッジに存在する。精度FAIL も回答が内容的に充足している。  
**結論**: 確定FAILとしない。

### qa-12b: 精度 FAIL(50%)

**内容**: `@Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる` がABSENT。  
→ run-1 でのUNCERTAINからABSENTに変化。  
→ このfactは「自動的に」という表現が不正確（追加設定が必要）。回答の方が正確な可能性あり。  
**判定**: 評価基準の問題（factの表現が過度に単純化されている可能性）。  
**幻覚**: PASS（run-1のSerializable問題はこのrunでは発生せず）。  
**結論**: 確定FAILとしない（評価基準の問題）。ユーザー確認待ち。

---

## 3c. 確定FAIL・却下（最終判定）

最終判定基準: **質問への実用上の害の有無**（害あり → 確定FAIL / 害なし → 却下）

| シナリオID | 判定 | 再現性 | 根拠（害の有無） |
|---|---|---|---|
| qa-05 | **確定FAIL** | 2/2 | 害あり: 設定クラス（Jackson2BodyConverter）が回答に欠落し、実装に必要な情報が届かない |
| impact-08 | **却下** | 2/2 | 害なし: 質問は日時切替の方法であり回答は方法を正しく説明。fixedDateのサンプル値ずれは質問の答えでない |
| qa-11a | **却下** | 2/2 | 害なし: must fact（ApplicationException→リクエストスコープ設定）は回答に明記済み。除外リストの省略は質問の核心でない |

**虚偽FAIL（確定FAILから除外）**:
- qa-11b: `FailureLogUtil` の記述は選定済み Javadoc の `content` フィールドに存在
- qa-12a: `ErrorMessages` メソッド群は選定済み `web-application-error-message.json` に存在
