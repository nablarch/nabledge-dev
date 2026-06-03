# ベンチマーク結果: v2-javadoc (In Progress — run-2 完了)

## 概要

**目的**: Javadoc 知識追加（Issue #363）による既存シナリオの精度維持確認 + 新シナリオ3件（qa-16/17/18）のPASS確認

**ラベル**: `v2-javadoc`（前回: `baseline-current`）

**状態**: run-1 完了 / run-2 完了 / run-3 未実施

---

## run-1 結果サマリー（旧30件）

| 項目 | 件数 |
|---|---|
| 実行シナリオ数 | 30（qa-16/17/18なし） |
| 完了 | 28 |
| ERROR | 2（qa-04, qa-15） |

### 精度（accuracy）

| 結果 | 件数 |
|---|---|
| PASS | 26/28 |
| FAIL | 1（qa-05: Jackson2BodyConverter ABSENT） |
| UNCERTAIN | 1（qa-12b） |

### ハルシネーション

| 結果 | 件数 |
|---|---|
| PASS | 20/28 |
| FAIL | 8/28 |

---

## run-2 結果サマリー（新33件全件）

| 項目 | 件数 |
|---|---|
| 実行シナリオ数 | 33（qa-16/17/18含む） |
| 完了 | 32 |
| ERROR | 1（review-09: MarkerError） |

### 精度（accuracy）

| 結果 | 件数 |
|---|---|
| PASS | 29/32 |
| FAIL | 3（qa-05, qa-12a, qa-12b） |

### ハルシネーション

| 結果 | 件数 |
|---|---|
| PASS | 26/32 |
| FAIL | 5（impact-08, qa-01, qa-11a, qa-11b, qa-12a） |

---

## 問題項目の評価

### run-1 問題

#### 1. qa-04: ERROR（タイムアウト）— run-2で解消

- **run-1**: claudeコマンドが360秒でタイムアウト
- **run-2**: 正常完了（PASS/PASS、10セクション、6ターン）
- **評価**: **揺らぎ（run-1のみ）**。run-2で再現しなかったため問題なし

#### 2. qa-15: ERROR（セクションID変化）— シナリオ修正で解消

- **原因**: PR #347（2026-05-22）でセキュリティチェックリストが再構成（s21→s5）
- **対処**: シナリオのセクションIDをs21→s5に修正済み（`fc6a43675`）
- **run-2**: 正常完了（PASS/PASS）
- **評価**: **解消済み**

#### 3. qa-05: 精度FAIL（Jackson2BodyConverter ABSENT）— 継続

- **状況**: mustクレーム3件中1件「JSONのコンバータにはJackson2BodyConverterが設定される」がABSENT（run-1/2共通）
- **根本原因**: スキルが `adapters-jaxrs-adaptor.json` を検索候補に含めなかった（3 run全て）
- **事前調査**: baseline-current でも同様に検索候補に含まれていなかった（`qa-current.json` ではこのfactが除外されていたため不問だった）
- **評価**: **Javadoc追加による新規退行ではない**。qa.json に Jackson2BodyConverter のfactが追加されたことで顕在化した既存課題。確定FAIL

#### 4. qa-12b: UNCERTAIN → FAIL（@Valid 動作の記述問題）— 揺らぎ

- **run-1**: UNCERTAIN（「自動的にエラーレスポンスになる」の判定保留）
- **run-2**: FAIL（ABSENT — 回答がデフォルト動作は空ボディと明記）
- **factの問題**: 「@Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる」はやや不正確。実際は `ErrorResponseBuilder` を使わないとメッセージが入らない
- **評価**: **評価基準の問題**。factの記述が「自動的に」と過剰に単純化しており、正確な回答を誤判定している。run-2の回答の方が正確。シナリオのfact修正が妥当

### run-2 新規問題

#### 5. qa-12a: 精度FAIL（エラー表示タグ ABSENT）— 揺らぎ

- **run-1**: PASS（`<n:errors>` タグについて正常に言及）
- **run-2**: FAIL（`<n:errors>` タグをThymeleaf優先の説明で「選択肢の一つ」として記述）
- **評価**: **揺らぎ**。run-1ではPASS。回答の強調点が変わったことで判定が揺れた。確定FAILとしない

#### 6. review-09: ERROR（MarkerError）— 揺らぎ

- **エラー**: `Workflow Details section not found in response`
- **run-1**: 正常完了（PASS/PASS）
- **評価**: **揺らぎ**。claude応答のフォーマット不正が一時的に発生。確定ERRORとしない

### ハルシネーション FAIL の評価

| シナリオ | run-1 | run-2 | 評価 |
|---|---|---|---|
| impact-01 | FAIL | PASS | 揺らぎ |
| impact-08 | FAIL | FAIL | 継続調査（run-3で確認） |
| qa-01 | PASS | FAIL | 揺らぎ |
| qa-10 | FAIL | PASS | 揺らぎ |
| qa-11a | FAIL | FAIL | 継続（run-3で確認） |
| qa-11b | FAIL | FAIL | 継続（run-3で確認） |
| qa-12a | FAIL | FAIL | 継続（run-3で確認） |
| qa-12b | FAIL | PASS | 揺らぎ |
| qa-13 | FAIL | PASS | 揺らぎ |

---

## 確定FAIL（run-2時点）

| シナリオ | 軸 | 分類 | 備考 |
|---|---|---|---|
| qa-05 | 精度 | 既存課題顕在化 | Jackson2BodyConverter未収録。Javadoc追加とは無関係 |

---

## baseline-current との比較（暫定、run-2終了時点）

| 軸 | baseline-current 3run平均 | run-1 | run-2 |
|---|---|---|---|
| 精度 PASS率 | 83.7% | 92.9%（26/28） | 90.6%（29/32） |
| ハルシネーション PASS率 | 14.4% | 71.4%（20/28） | 81.3%（26/32） |

**注意**: 3 run完了後に再集計する。

---

## 次のアクション

1. **run-3 実行**（33件全件）
2. **run-3完了後**: 3 run集計 + baseline-current 比較
