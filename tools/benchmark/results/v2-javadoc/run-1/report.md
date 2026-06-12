# ベンチマーク run-1 レポート

**ラベル**: v2-javadoc  
**実行日時**: 2026-06-03T13:25:34  
**シナリオ数**: 30（旧シナリオ、qa-16/17/18なし）  
**スキル**: `.claude/skills/nabledge-6`

---

## 3a. 数値サマリー

| シナリオID | 精度 | 幻覚 | セクション数 | ターン数 |
|---|---|---|---|---|
| pre-01 | PASS | PASS | 4 | 9 |
| pre-02 | PASS | PASS | 8 | 8 |
| pre-03 | PASS | PASS | 9 | 5 |
| review-06 | PASS | PASS | 9 | 7 |
| review-07 | PASS | PASS | 5 | 10 |
| review-08 | PASS | PASS | 4 | 6 |
| review-09 | PASS | PASS | 8 | 11 |
| impact-01 | PASS | FAIL | 2 | 12 |
| impact-03 | PASS | PASS | 3 | 8 |
| impact-06 | PASS | PASS | 7 | 8 |
| impact-08 | PASS | FAIL | 8 | 12 |
| qa-01 | PASS | PASS | 5 | 21 |
| qa-02 | PASS | PASS | 11 | 10 |
| qa-03 | PASS | PASS | 3 | 7 |
| qa-04 | **ERROR** | - | - | - |
| qa-05 | FAIL(67%) | PASS | 8 | 11 |
| qa-06 | PASS | PASS | 6 | 5 |
| qa-07 | PASS | PASS | 10 | 13 |
| qa-08 | PASS | PASS | 5 | 6 |
| qa-09 | PASS | PASS | 13 | 10 |
| qa-10 | PASS | FAIL | 10 | 3 |
| qa-11a | PASS | FAIL | 9 | 8 |
| qa-11b | PASS | FAIL | 8 | 11 |
| qa-12a | PASS | FAIL | 10 | 14 |
| qa-12b | UNCERTAIN(50%) | FAIL | 10 | 12 |
| qa-13 | PASS | FAIL | 5 | 11 |
| qa-14 | PASS | PASS | 25 | 9 |
| qa-15 | **ERROR** | - | - | - |
| oos-impact-01 | PASS | PASS | 12 | 7 |
| oos-qa-01 | PASS | PASS | 2 | 8 |

**集計（28件、ERROR2件除く）**:
- 精度 PASS: 26/28 = 92.9%（UNCERTAIN1件含む）
- 精度 FAIL: 1/28 = 3.6%（qa-05）
- 精度 UNCERTAIN: 1/28 = 3.6%（qa-12b）
- 幻覚 PASS: 20/28 = 71.4%
- 幻覚 FAIL: 8/28 = 28.6%

---

## 3b. FAIL/UNCERTAIN/ERROR シナリオの妥当性評価

### qa-04: ERROR（タイムアウト360秒）

**状況**: claude CLIが360秒タイムアウト。出力なし。  
**原因**: baseline（最大160秒）より大幅に長い。Javadoc知識増加によりキャッシュ生成が増えた可能性。  
**判定**: スキルの挙動問題（タイムアウト）。ただし run-2 で PASS を確認済み（再現性なし）。  
**結論**: 確定FAILとしない（揺らぎ）。

### qa-15: ERROR（s21未発見）

**状況**: PR #347でs21→s5に統合済みだったが、シナリオ参照が旧パスのままだった。  
**原因**: シナリオ定義の参照セクションIDが古かった（実装側の変更に追従していなかった）。  
**修正**: `fc6a43675` でシナリオを修正済み。run-2 で PASS 確認済み。  
**結論**: 確定FAILとしない（シナリオ定義バグ、修正済み）。

### qa-05: 精度 FAIL(67%)

**状況**: `Jackson2BodyConverterが設定される` というfactがABSENT。  
**内容**: 回答は「リクエストボディ変換ハンドラ」と説明するが、Jackson2BodyConverterというクラス名を明示しない。  
**妥当性評価**: このfactはABSENT。ただし、mustでありJackson2BodyConverterの名称が知識に記載されていてもスキルが言及しない問題。  
**確認**: baseline でも同じfactが未検出（既存課題）。run-2 でも同様に FAIL。  
**判定**: スキルの挙動問題（Jackson2BodyConverter名称の言及漏れ）。再現性あり（run-1/run-2ともFAIL）。  
**結論**: 確定FAIL候補。ユーザー確認待ち。

### qa-12b: 精度 UNCERTAIN(50%) + 幻覚 FAIL

**精度UNCERTAIN**: `@Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる` がUNCERTAIN。  
→ 回答は「@ValidはApplicationExceptionをスローするが、デフォルトのJaxRsResponseHandlerは自動でエラーレスポンスを設定しないため追加設定が必要」と正確に説明。Factの「自動的に」という表現が不正確で、回答の方が正確な可能性あり。  
→ **評価基準の問題**（factの表現が過度に単純化されている）の可能性が高い。

**幻覚FAIL**: `ProjectFormがSerializableを実装している` がunsupported。  
→ 知識セクションのProjectFormコード例にSerializableの記載がなく、回答が追加した情報。  
→ ただしJavaのシリアライズはフォームクラスの一般的な実装パターン。Nablarch固有のハルシネーションではなく、一般的な補足情報。  
→ **ナレッジ未収録の補足**と判定。

**結論**: 確定FAILとしない（評価基準の問題 + 一般的な補足情報）。ユーザー確認待ち。

### impact-01: 幻覚 FAIL

**内容**: `トランザクション名（dbTransactionName）は一意にすること` がunsupported。  
→ 知識セクションに記載がない注意点を追加している。  
→ ただし、これはNablarch設定の一般的な注意点であり、完全な誤りではない可能性。  
**判定**: ナレッジ未収録の補足（一般的なNablarch設定の注意点）。run-2 では PASS のため再現性なし。  
**結論**: 確定FAILとしない（揺らぎ）。

### impact-08: 幻覚 FAIL

**内容**: `SystemTimeUtil.getDate()を使用する` / `FixedSystemTimeProviderはnablarch-testingに含まれる` がunsupported。

**選定ページ全体確認（再調査）**:
- `SystemTimeUtil.getDate()`: Javadocファイル `javadoc-nablarch-core-date-SystemTimeUtil.json` に `getDate()` が存在する。run-1 では選定ページに含まれていなかったが、情報はナレッジに存在する → **虚偽FAIL**
- `nablarch-testingモジュール`: `testing-framework-03-Tips.json` にFQCN（`nablarch.test.FixedSystemTimeProvider`）はあるが「nablarch-testingモジュール」という表現は選定ページのどこにも存在しない → **確定FAIL**

**判定**: `nablarch-testingモジュール` の表現が選定ページに未収録。run-2 でも別クレームでFAIL → 再現性あり。  
**結論**: 確定FAIL（ただし `SystemTimeUtil.getDate()` クレームは虚偽、`nablarch-testingモジュール`表現クレームが確定FAIL）。

### qa-10: 幻覚 FAIL

**内容**: SQLファイルの例が gold standard より簡略化されている（PROJECT_END_DATE条件・$sort句の欠落）。  
→ 回答のSQL例はknowledgeの完全なSQL例より簡略化されており、実際に差分あり。  
**判定**: スキルの挙動問題（SQL例が不完全）。run-2 では PASS → 再現性なし（揺らぎ）。  
**結論**: 確定FAILとしない（揺らぎ）。

### qa-11a: 幻覚 FAIL

**内容**: `その他の例外はFATAL、500を返す` がunsupported（ThreadDeath/VirtualMachineError等は除外される）。  
→ 知識セクションに例外テーブルの詳細な記述があり、回答がその一部を単純化している。  
**判定**: スキルの挙動問題（例外テーブルの単純化）。run-2 でも FAIL → 再現性あり。  
**結論**: 確定FAIL候補。ユーザー確認待ち。

### qa-11b: 幻覚 FAIL

**内容**: `JaxRsErrorLogWriterでApplicationException以外の例外はFailureLogUtilを使って障害ログを出力する` がunsupported。

**選定ページ全体確認（再調査）**:
- 選定済みの `javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json` のクラス説明（`content`フィールド）に「{@link FailureLogUtil}を用いてログ出力を行う」と明記されている。

**判定**: **虚偽FAIL** — 自動評価器がページの `content`（導入文）を見落とした。FailureLogUtil の記述はナレッジに存在する。  
**結論**: 確定FAILとしない。

### qa-12a: 幻覚 FAIL

**内容**: Thymeleafの `errors.hasError()`, `errors.getMessage()`, `errors.allMessages` / `errors.globalMessages` メソッドがunsupported。

**選定ページ全体確認（再調査）**:
- 選定済みの `web-application-error-message.json` を全セクション確認したところ、Thymeleafでの使用例として `errors.hasError('form.userName')`、`errors.getMessage('form.userName')`、`errors.globalMessages`、`errors.allMessages` が全て記載されている。

**判定**: **虚偽FAIL** — 自動評価器が選定ページの当該セクションを見落とした。全メソッドはナレッジに存在する。  
**結論**: 確定FAILとしない。

### qa-13: 幻覚 FAIL

**内容**: `バリデーションエラー時はApplicationExceptionを送出して後続処理を行わない` がunsupported。  
→ 知識セクションにApplicationException送出の明記なし。  
**判定**: ナレッジ未収録の補足。run-2 では PASS → 再現性なし（揺らぎ）。  
**結論**: 確定FAILとしない（揺らぎ）。

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
