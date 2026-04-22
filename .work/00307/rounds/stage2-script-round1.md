# Stage 2 Script Judge — Round 1 (2026-04-22)

初回の **正解ベース採点**（模範回答の citation vs filter 候補の `in` 判定）。既存の 30 件ベースライン結果を再利用、判定のみやり直し。

## 計測条件

- **Date**: 2026-04-22
- **Results dir (source)**: `tools/benchmark/.results/20260422-143411-stage3-sonnet/`
- **Reference answers**: `tools/benchmark/scenarios/qa-v6-answers/*.md` (30件)
- **Grading**: `tools/benchmark/grading/reference_answer.py` + `score_stage2.py`
- **Threshold**: 1.0→3 / ≥0.67→2 / ≥0.33→1 / <0.33→0
- **判定単位**: ファイルパス（section は Stage 3 で見る）
- **出力**: `.results/20260422-143411-stage3-sonnet/stage2_script.json`

## 結果サマリー

| 指標 | 値 |
|-----|---|
| level=3 率 | **25/30 (83%)** |
| level≥2 率 | **27/30 (90%)** |
| level 分布 | `{0:1, 1:2, 2:2, 3:25}` |

## 落ちた 5 件の内訳

| id | level | coverage | 欠落パス | 観察 |
|---|---|---|---|---|
| impact-06 | **0** | 0/2 | `component/handlers/handlers-secure_handler.json`、`component/libraries/libraries-tag.json` | CSP + JSP 書換え。facet=`web-application/security-check` のみ、`libraries` が出ていない |
| req-06 | **1** | 1/3 | `component/libraries/libraries-session_store.json`、`component/libraries/libraries-stateless_web_app.json` | スケールアウト設計。facet に `libraries` が含まれず、`cloud-native` 止まり |
| review-05 | **2** | 2/3 | `component/handlers/handlers-jaxrs_response_handler.json` | REST エラー応答。facet=`restful-web-service/libraries` で `handlers` 欠落 |
| review-07 | **2** | 2/3 | `component/libraries/libraries-tag.json` | CSP 設定。facet=`web-application/security-check/handlers` で `libraries` 欠落 |
| review-10 | **1** | 1/2 | `about/about-nablarch/about-nablarch-nablarch_api.json` | バージョンアップ。facet=`check/development-tools/security-check/java-static-analysis` で `about-nablarch` 欠落 |

## パターン分析

3 つのパターンに分類できる:

### A. facet に `libraries` が出ていない（impact-06 / req-06 / review-07 — 3件）

- **impact-06** (CSP + JSP 書き換え): 質問が「セキュリティ対策」「JSP 書き方」中心で、ハンドラよりライブラリ側のタグ機能が必要だが、facet 抽出が `security-check` でとまる
- **req-06** (スケールアウト設計): `stateless_web_app`（library）と `session_store`（library）が該当するが、facet は `cloud-native`/`handlers`/`web-application` どまり
- **review-07** (CSP 設定): 同じく `libraries-tag.json` が必要だが facet に `libraries` が出ない

**仮説**: AI-1 facet 抽出プロンプトに「機能が tag / libraries 側にあるケースを見逃しやすい」という弱点がある。

### B. facet に `handlers` が出ていない（review-05 — 1件）

- **review-05** (REST エラー応答): facet=`restful-web-service/libraries` で `jaxrs_response_handler`（handlers カテゴリ）が欠落

**仮説**: 「エラー応答」→ ハンドラという対応が facet 抽出で取れていない。

### C. facet に `about-nablarch` / メタカテゴリが出ない（review-10 — 1件）

- **review-10** (バージョンアップ対応): `about/about-nablarch/about-nablarch-nablarch_api.json` は "Nablarch について" のメタ情報ファイル。facet 抽出で「Nablarch 自体の情報」カテゴリが取れていない

**仮説**: 質問が「バージョンアップで壊れない」という業務語彙で、メタカテゴリに到達しない。これは構造的に難しい可能性がある。

## 次のアクション

**オプション 1**: AI-1 facet 抽出プロンプトを改訂して `libraries` / `handlers` をより広めに出させる。ただし precision が下がり candidate 数が増える可能性。

**オプション 2**: filter の fallback ladder を見直す。現状は type×category の AND 絞込みだが、coverage が微妙なケース用に OR fallback を追加。

**オプション 3**: 30/30 を目指すのではなく、**level≥2 で 90%** は実用上問題ないと判断し、Stage 3 judge（模範回答ベース）に進む。落ちた 5 件は Stage 3 でどう振る舞うか次第で再検討。

**推奨**: **オプション 3**。Stage 2 は precision なくファイル到達の recall を測る段階で、90% の部分到達率は「filter 設計として妥当」と言える。落ちた 5 件の Stage 3 挙動（生成回答の品質）を見てから、Stage 2 改善か Stage 3 許容かを判断する方が情報が増える。
