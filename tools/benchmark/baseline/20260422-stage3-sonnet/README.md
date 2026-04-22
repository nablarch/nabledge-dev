# Baseline: Stage 3 — 30 scenarios (Sonnet, 2026-04-22)

## 条件

- **Date**: 2026-04-22
- **Scenarios**: qa-v6.json (30件 — review 10 / impact 10 / req 10)
- **Model**: Sonnet (AI-1 / AI-2 / AI-3 / judge すべて)
- **Prompts**:
  - stage1_facet.md (Round 3)
  - stage3_section_select.md (PE-reviewed + Round 1 fix)
  - stage3_answer.md (PE-reviewed + Round 1 fix)
  - judge_stage3.md (PE-reviewed + Round 1 fix)

## 結果サマリー

| 指標 | 値 |
|-----|---|
| judge=3 率 | **30/30 (100%)** |
| judge 分布 | `{0:0, 1:0, 2:0, 3:30}` |
| fallback=none | 全30件 |
| mean candidates | 81.8行 |
| mean picks (AI-2) | 5.3セクション |
| mean cost | $0.528/件 ($15.83 合計) |
| mean wall | 82.7s/件 (41.4分 合計・逐次) |

## 注目ケース

- **review-10**: candidates=2 (最少)、picks=1。極端な絞込みでも judge=3。
- **impact-06**: candidates=23、picks=3。CSP/JSP 書き換えの not-built-in 系。
- **impact-02/05/07/10、req-01/02/04**: candidates=124 (最大)。広い候補でも AI-2 が5〜8に絞込み。

## 用途

このベースラインは新しいフロー（ファセット検索）の初期計測値。
本番 skill 反映後に同じ30件で再計測し、改善/後退を比較する。
