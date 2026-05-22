# ベンチマーク結果: v1-new-search (3 runs)

**Skill**: nabledge-6 (new search: keyword-search + semantic-search)  
**Scenarios**: `tools/benchmark/scenarios/qa.json` (30シナリオ)  
**Date**: 2026-05-21〜22

---

## ステップ4: 3 run集計

### 4a. 3 run集計

| 軸 | run-1 | run-2 | run-3 | 平均 |
|---|---|---|---|---|
| 精度 PASS率 | 96.7% (29/30) | 96.7% (29/30) | 93.3% (28/30) | **95.6%** |
| 幻覚 PASS率 | 93.3% (28/30) | 86.7% (26/30) | 86.7% (26/30) | **88.9%** |
| コスト合計 | $27.56 | $25.94 | $28.25 | $27.25/run |

確定FAIL一覧（3 run中で1回以上 confirmed FAIL となったシナリオ）:

| シナリオID | FAIL回数/3 | 分類 |
|---|---|---|
| qa-05 | 1/3 (run-3) | スキルの挙動問題: JaxbBodyConverterをapplication/json用と誤説明（正: application/xml用） |

### 4b. 前回ラベル（baseline-current）との比較

| 軸 | baseline-current 平均 | v1-new-search 平均 | 差分 |
|---|---|---|---|
| 精度 PASS率 | 83.7% | 95.6% | **+11.9pp** |
| 幻覚 PASS率 | 14.4% | 88.9% | **+74.5pp** |
| コスト/run | $19.78/run | $27.25/run | +$7.47/run (+37.8%) |

> **注**: baseline-current の幻覚PASS率が低いのは、旧検索で少ない/間違いセクションを読んだため多くの未支持クレームが発生していたため。新検索（keyword+semantic）でグラウンディングが大幅改善。

---

## シナリオ別 3 run 結果

| シナリオID | run-1 精度 | run-1 幻覚 | run-2 精度 | run-2 幻覚 | run-3 精度 | run-3 幻覚 |
|---|---|---|---|---|---|---|
| pre-01 | PASS | PASS | PASS | PASS | PASS | PASS |
| pre-02 | PASS | PASS | PASS | PASS | PASS | UNCERTAIN* |
| pre-03 | PASS | PASS | PASS | PASS | PASS | PASS |
| review-06 | PASS | PASS | PASS | PASS | PASS | PASS |
| review-07 | PASS | PASS | PASS | PASS | PASS | PASS |
| review-08 | PASS | PASS | PASS | FAIL* | PASS | PASS |
| review-09 | PASS | PASS | PASS | PASS | PASS | PASS |
| impact-01 | PASS | PASS | PASS | PASS | PASS | PASS |
| impact-03 | PASS | PASS | PASS | FAIL* | PASS | PASS |
| impact-06 | PASS | PASS | PASS | PASS | PASS | PASS |
| impact-08 | PASS | FAIL* | PASS | PASS | PASS | FAIL* |
| qa-01 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-02 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-03 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-04 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-05 | PASS | PASS | PASS | PASS | PASS | **CONFIRMED FAIL** |
| qa-06 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-07 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-08 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-09 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-10 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-11a | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-11b | PASS† | PASS | PASS† | PASS | PASS† | PASS |
| qa-12a | PASS | UNCERTAIN* | PASS | FAIL* | PASS | PASS |
| qa-12b | UNCERTAIN† | PASS | UNCERTAIN† | FAIL* | UNCERTAIN† | PASS |
| qa-13 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-14 | PASS | PASS | PASS | PASS | PASS | PASS |
| qa-15 | PASS | PASS | PASS | PASS | PASS | UNCERTAIN* |
| oos-impact-01 | PASS | PASS | PASS | PASS | PASS | PASS |
| oos-qa-01 | PASS | PASS | PASS | PASS | PASS | PASS |

凡例:
- `*` : 妥当性評価で「問題なし」と判定（確定FAILではない）
- `†` : claimの過単純化によるUNCERTAIN（回答品質ではなくfact記述の問題）
- **CONFIRMED FAIL**: ユーザー承認済みの確定FAIL

---

## 確定FAIL詳細

### qa-05 (run-3のみ)

**原因**: JaxbBodyConverterをapplication/json用のコンバータと誤説明。  
**根拠**: `handlers-body-convert-handler.json:s4` でapplication/xml用であると明示されている。JSON用コンバータの設定例はナレッジ未収録のため、スキルが誤った補完を行った。  
**再現性**: 1/3（run-1/2はPASS） → 揺らぎ候補だが事実誤認のため確定FAIL

---

## 妥当性評価サマリー（auto FAIL/UNCERTAIN → 問題なし と判定した案件）

| シナリオ | run | auto判定 | 最終判定 | 理由 |
|---|---|---|---|---|
| impact-08 | 1,3 | Hal FAIL | 問題なし | RSTの誤記（12桁/15桁→正: 14桁/17桁）。回答が正確 |
| review-08 | 2 | Hal FAIL | 問題なし | 不支持クレームの内容はナレッジs3に明示されており正確 |
| impact-03 | 2 | Hal FAIL | 問題なし | ApplicationException→ErrorResponse生成はナレッジから合理的に導出可能 |
| qa-12a | 1 | Hal UNCERTAIN | 問題なし | Thymeleaf補足情報はナレッジ未収録だが一般的。Nablarch固有のハルシネーションではない |
| qa-12a | 2 | Hal FAIL | 問題なし | run-1と同判定 |
| qa-12b | 2 | Hal FAIL | 問題なし | Required.messageキー名はナレッジ記載あり。値差は例示レベル |
| pre-02 | 3 | Hal UNCERTAIN | 問題なし | Thymeleaf補足情報（qa-12aと同じパターン） |
| qa-15 | 3 | Hal UNCERTAIN | 問題なし | デフォルトヘッダ値はナレッジ未記載の補足情報 |
| qa-12a | 3 | Acc 0.0 | 問題なし | mustの「HttpErrorHandler言及」は purpose=実装したい に対して過剰 |
| qa-12b | 1,2,3 | Acc UNCERTAIN | 問題なし | factの過単純化（回答はより正確） |

---

## 既知の問題（Known Issues）

- **公式ドキュメント誤記**: `06_TestFWGuide/03_Tips.rst` の fixedDate フォーマット桁数が誤記（「12桁」「15桁」→正しくは「14桁」「17桁」）。impact-08のHal FAILはこの誤記に起因。

---

## ステップ5: 確定FAILの根本原因調査

### qa-05: JaxbBodyConverter 誤説明

**再現性**: 1/3 (run-3のみ)

**原因分類**: スキルの挙動問題

**根本原因**:

run-3はBodyConvertHandlerの設定例（`handlers-body-convert-handler.json:s4`）を読んだ。s4の設定例には以下のコメントが含まれている:
```xml
<!-- application/xmlに対応したリクエスト・レスポンスのコンバータ -->
<component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
```

しかしrun-3の回答では、ユーザー質問が「JSON登録」のため、スキルがJaxbBodyConverterをapplication/json用と誤解釈し、設定例のXMLコメントを書き換えて回答した:
```xml
<!-- application/jsonに対応したコンバータ -->
<component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
```

**run-1/2がPASSだった理由**: run-1はs4（設定例）を読まなかったため、JaxbBodyConverterの言及がなかった。run-2も同様にs4を選択しなかったかコンバータ設定に言及しなかった。

**改善可能性**:
- ナレッジ未収録: application/json用コンバータ（`JacksonBodyConverter`相当）の設定例がナレッジに存在しない
- s4のコメントを読んでも「xml用なのにjsonに使えるか」という判断は困難
- 1/3の発生率は揺らぎに近いが、事実誤認（xml用をjson用と提示）のため品質問題

**提案**:

| 項目 | 内容 |
|---|---|
| 原因分類 | スキルの挙動問題（ナレッジ未収録 + LLM誤補完） |
| 再現性 | 1/3（揺らぎ候補） |
| 提案 | 対処不要（揺らぎ扱い）または要改善（ナレッジにjson用コンバータ例を追加） |
| 根拠 | 1/3の発生率。ただし発生時の誤りは明確な事実誤認（xml→json誤記）のため、ナレッジ補強で根本解決可能 |

→ **ユーザーが対応要否を判定**
