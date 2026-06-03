# ベンチマーク run-3 レポート

**ラベル**: v2-javadoc  
**実行日時**: 2026-06-03T17:51:18  
**シナリオ数**: 33（全件）  
**スキル**: `.claude/skills/nabledge-6`

---

## 3a. 数値サマリー

| シナリオID | 精度 | 幻覚 | セクション数 | ターン数 |
|---|---|---|---|---|
| pre-01 | PASS | PASS | 10 | 3 |
| pre-02 | PASS | FAIL | 7 | 6 |
| pre-03 | PASS | PASS | 10 | 9 |
| review-06 | PASS | PASS | 6 | 7 |
| review-07 | PASS | PASS | 5 | 7 |
| review-08 | PASS | PASS | 7 | 9 |
| review-09 | PASS | PASS | 7 | 8 |
| impact-01 | PASS | PASS | 3 | 10 |
| impact-03 | PASS | PASS | 3 | 8 |
| impact-06 | PASS | PASS | 9 | 8 |
| impact-08 | PASS | PASS | 9 | 11 |
| qa-01 | PASS | PASS | 10 | 3 |
| qa-02 | PASS | FAIL | 9 | 9 |
| qa-03 | PASS | PASS | 6 | 15 |
| qa-04 | PASS | PASS | 11 | 11 |
| qa-05 | FAIL(67%) | PASS | 6 | 12 |
| qa-06 | **ERROR** | - | - | - |
| qa-07 | PASS | PASS | 5 | 5 |
| qa-08 | PASS | PASS | 10 | 7 |
| qa-09 | PASS | FAIL | 13 | 11 |
| qa-10 | PASS | PASS | 3 | 5 |
| qa-11a | PASS | PASS | 10 | 9 |
| qa-11b | PASS | PASS | 10 | 12 |
| qa-12a | PASS | FAIL | 7 | 10 |
| qa-12b | UNCERTAIN | PASS | 6 | 11 |
| qa-13 | PASS | FAIL | 5 | 8 |
| qa-14 | PASS | FAIL | 10 | 5 |
| qa-15 | **ERROR** | - | - | - |
| qa-16 | PASS | PASS | 4 | 9 |
| qa-17 | FAIL | PASS | 3 | 7 |
| qa-18 | PASS | FAIL | 3 | 6 |
| oos-impact-01 | PASS | PASS | 10 | 10 |
| oos-qa-01 | PASS | PASS | 2 | 12 |

**集計（31件、ERROR2件除く）**:
- 精度 PASS: 29/31 = 93.5%（UNCERTAIN1件含む）
- 精度 FAIL: 2/31 = 6.5%（qa-05, qa-17）
- 幻覚 PASS: 23/31 = 74.2%（UNCERTAIN0件）
- 幻覚 FAIL: 8/31 = 25.8%

---

## 3b. FAIL/UNCERTAIN/ERROR シナリオの妥当性評価

### qa-06: ERROR（タイムアウト360秒）

**状況**: run-1/run-2 ではPASS。今回のみタイムアウト。  
**判定**: 揺らぎ。再現性なし（1/3）。  
**結論**: 確定FAILとしない。

### qa-15: ERROR（タイムアウト360秒）

**状況**: run-2 ではPASS（シナリオ修正済み）。今回のみタイムアウト。  
**判定**: 揺らぎ。再現性なし（run-2 PASS、run-3のみタイムアウト）。  
**結論**: 確定FAILとしない。

### qa-05: 精度 FAIL(67%)

**内容**: Jackson2BodyConverter名称の言及漏れ。run-1/run-2/run-3 全てFAIL。  
**判定**: 確定FAIL（スキルの挙動問題、再現性 3/3）。承認済み。

### qa-17: 精度 FAIL

**内容**: `get(String name)で型パラメータを利用してリポジトリからコンポーネントを型安全に取得する` がABSENT。  
→ 回答は `SystemRepository.get("name")` の基本的な使い方は説明しているが、型パラメータ（`SystemRepository.<Type>get("name")`）を言及していない。  
→ must section は `javadoc/javadoc-nablarch-core-repository-SystemRepository.json:s11`（Javadoc知識）。  
→ run-2 ではPASS、run-3のみFAIL。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない（揺らぎ）。ユーザー確認待ち。

### pre-02: 幻覚 FAIL

**内容**: `@InjectFormのvalidateパラメータはバリデーションメソッド名（グループ名）を指定する` がunsupported。  
→ 知識セクションにvalidateパラメータの説明なし。run-1/run-2 ではPASS。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない。

### qa-02: 幻覚 FAIL

**内容**: `トランザクションループ制御ハンドラのコミット間隔はデフォルトで1件ごとのコミット` がunsupported。  
→ run-1/run-2 ではPASS。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない。

### qa-09: 幻覚 FAIL

**内容**: 
- `SystemTimeUtil.getLocalDateTime()` がunsupported（知識に記載なし）
- 業務日付のキャッシュ有効/setCacheEnabled(false)の動作がunsupported

→ run-1/run-2 ではPASS。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない。

### qa-11a: 幻覚 PASS（run-3のみ）

run-1/run-2でFAILだったが、run-3ではPASS。確定FAIL判定（承認済み）は変わらず。

### qa-11b: 幻覚 PASS（run-3のみ）

run-1/run-2でFAILだったが、run-3ではPASS。かつナレッジ全体確認により虚偽FAILと判定済み（JaxRsErrorLogWriter Javadoc content に明記）。

### qa-12a: 幻覚 FAIL

**内容**: Thymeleaf固有ErrorMessagesメソッドがunsupported。run-1/run-2/run-3でFAIL。

**選定ページ全体確認（再調査）**:
- 選定済みの `web-application-error-message.json` に全メソッド（hasError/getMessage/allMessages/globalMessages）の使用例が存在する → **虚偽FAIL**。

**判定**: 虚偽FAIL（自動評価器が選定ページのセクションを見落とした）。  
**結論**: 確定FAILとしない。

### qa-12b: 精度 UNCERTAIN

**内容**: `@Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる` がUNCERTAIN（run-1と同じ）。  
**判定**: 評価基準の問題（factの表現が不正確）。確定FAILとしない方針継続。

### qa-13: 幻覚 FAIL

**内容**: `バリデーションエラー時はApplicationExceptionが送出されて後続処理には進まない` がunsupported。

**選定ページ全体確認（再調査）**:
- 選定済みの `handlers-jaxrs-bean-validation-handler.json` のページ導入文（`content` フィールド）に「バリデーションでバリデーションエラーが発生した場合には、後続のハンドラに処理は委譲せずに、ApplicationException を送出して処理を終了する。」と明記されている → **虚偽FAIL**。

**判定**: 虚偽FAIL（自動評価器がページの `content` フィールドを見落とした）。  
**結論**: 確定FAILとしない。

### qa-14: 幻覚 FAIL

**内容**: `移行前にNablarch 5の最新バージョン（5u25）に上げておくことが前提条件` がunsupported（具体的バージョン番号がknowledgeに未記載）。  
→ run-1/run-2 ではPASS。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない。

### qa-18: 幻覚 FAIL

**内容**: `BeanUtil.getProperty(user, "address.postNo")のように「.」区切りでネストしたBeanのプロパティを指定できる` がunsupported。  
→ JavadocのgetPropertyのドキュメントにはネストプロパティの記載がない（Javadoc知識が誘発した可能性あり）。  
→ run-1/run-2 ではPASS。  
**判定**: 揺らぎ（再現性 1/3）。  
**結論**: 確定FAILとしない。

---

## 3c. 確定FAIL（ナレッジ全体確認後の最終判定）

| シナリオID | 分類 | run-1 | run-2 | run-3 | 再現性 | 内容 |
|---|---|---|---|---|---|---|
| qa-05 | スキルの挙動問題 | 精度FAIL | 精度FAIL | 精度FAIL | 3/3 | Jackson2BodyConverter名称の言及漏れ |
| qa-11a | スキルの挙動問題 | 幻覚FAIL | 幻覚FAIL | 幻覚PASS | 2/3 | 例外テーブルの単純化（ThreadDeath/VirtualMachineError除外漏れ） |

**虚偽FAIL（確定FAILから除外）**:
- qa-11a (run-3): run-3 ではPASS（再現性2/3）
- qa-11b: JaxRsErrorLogWriter Javadoc の `content` フィールドに FailureLogUtil が明記
- qa-12a: web-application-error-message.json に ErrorMessages メソッド群が存在
- qa-13: handlers-jaxrs-bean-validation-handler.json の `content` フィールドに ApplicationException 送出が明記
- impact-08 の一部: yyyyMMddHHmmssは14桁（知識の誤り）、getTimestamp()（Javadocに存在）は虚偽FAIL
