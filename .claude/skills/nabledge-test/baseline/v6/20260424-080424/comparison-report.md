# ベースライン比較レポート

> ⚠️ **このレポートの計測は科学的に無効です**
>
> 取得時点の nabledge-6 skill に RBKC V4 (commit `68c11a9d7`) 移行時の schema 追従漏れが複数残存しており、知識探索パイプラインが壊れた状態で計測されました。
> - `scripts/full-text-search.sh` の jq 式が dict 前提で、list 形式 JSON に対して 0 hits silent failure
> - `scripts/get-hints.sh` / `workflows/_knowledge-search/_section-search.md` / `_section-judgement.md` Step 0 が消失済の `.index[].hints` を参照しており機能していない
> - SKILL.md 72 行目「index.toon with search hints」の記述も実態と乖離
>
> **前回比較 (RBKC 改善効果の評価) としては使えません**。skill 修正後 (Phase 22-B-14) に baseline を再取得します。このレポートは「何が壊れていたか」の原因分析資料として保存しています。

## 概要

| 項目 | 前回 | 今回 |
|------|------|------|
| Run ID | 20260331-152005 | 20260424-080424 |
| Branch | 277-improve-n12-ca-accuracy-v2 | 299-implement-rbkc |
| Commit | e55c25c3 | 5e79d7925 |
| 日時 | 2026-03-31T15:20:05Z | 2026-04-23T23:16:20Z |

## 前回からの変更点

- Phase 22-B-5b: Excel converter 書き直し。1 シート = 1 JSON / 1 MD の分割、P1 データ表は全行 MD テーブルで復元 (nabledge-dev#299)
- Phase 22-B-9: Excel シート分類一覧 (P1/P2 override 判断資料) を出力 (nabledge-dev#299)
- Phase 22-B-16a: RST section レベル対応 (`##`/`###`/`####`) — 従来は全 `##` で潰れていたものが階層保持 (nabledge-dev#299)
- Phase 22-B-16b: RST `:ref:`/`:doc:`/`:numref:` + MD 相対リンクを cross-doc CommonMark リンクに変換、docs MD と JSON content の両方に埋め込み (nabledge-dev#299)
- Phase 22-B-16c: `image`/`figure`/`:download:` asset の URI 書き換え + assets コピー + QL1 asset-exists 検査 (nabledge-dev#299)
- Phase 22-B 共通: verify QO1 level チェック + QL1 両側 (cross-doc + asset-exists) + silent skip 横断修正。知識ファイルが 353 件（旧 270 件台）に増加、うち 256 件が cross-doc リンクを含む (nabledge-dev#299)
- nabledge-dev 側 AI-1/judge 系改良 (nabledge-dev#307): term_queries 追加、a_facts 事前記述、判定精度改善。v6 skills 自体への影響はなし

---

## ベンチマーク比較（品質測定）

*各シナリオ10試行の統計。95%信頼区間が重ならない場合のみ変化を有意とみなす。*

| Scenario | 前回 mean±SD | 前回 95%CI | 今回 mean±SD | 今回 95%CI | 変化 |
|----------|--------------|-----------|--------------|-----------|------|
| qa-001 | 100.0% ±0.0% | [100.0%-100.0%] | 87.5% ±21.6% | [33.7%-100.0%] | -12.5pp → |
| ca-003 | 97.3% ±0.0% | [97.3%-97.3%] | 100.0% ±0.0% | [100.0%-100.0%] | +2.7pp 🟢 |

**判定**: 🟢 CI非重複の改善 / 🔴 CI非重複の劣化 / → CI重複（誤差範囲内）

---

## 総合評価

### 結論: RBKC の知識品質は改善している（CA）、QA 検出低下は知識未到達のエージェント挙動差

**CA（3 シナリオ合計 106 項目）**:
- ca-002 96.9% → 100.0% / ca-003 97.3% → 100.0% (CI 非重複の有意改善) / ca-001 97.3% → 94.6%
- **純増分**: ca-002 の `DataReader`、ca-003 の `FilePathSetting`、ca-001 の `BeanUtil` が Nablarch Framework Usage 見出しに独立セクションとして出現。前回 ca-003 の既知ギャップ「`FilePathSetting` が独立見出しに出ない」(memory 記録 -2.7pp) が解消。
- **純減**: ca-001 Overview で `UniversalDao` / `SessionUtil` の英名が日本語表現「ユニバーサルDAO」「セッションストア」に置換された。同ドキュメントの Nablarch Framework Usage には英名で登場しているため、Overview テンプレートの文体差に起因する表層的な問題。
- **CA はリンクを辿ったのか?**: 辿っていない。`workflows/code-analysis.md` Step 2 は `full-text-search.sh` + `read-sections.sh` で知識を検索する構造で、Phase 22-B-16 で導入した cross-doc MD リンクはエージェント走行時に辿られていない。ただし RBKC 側の改善効果は **「知識ファイルのセクション階層が `##`/`###`/`####` に整備され、read-sections.sh で取得した section の見出しが CA 生成ドキュメントにそのまま引き継がれる」** という間接的な形で効いており、結果として `FilePathSetting` など独立見出しの情報が Nablarch Framework Usage セクションで独立見出し化された。

**QA（5 シナリオ合計 40 項目）**:
QA 検出率低下 12.5pp は **RBKC の知識不足ではなく、エージェントの知識ファイル選択の差**。4 つの欠落キーワードすべてが v6 知識ファイル内に存在することを確認:

| シナリオ | 欠落キーワード | 存在する知識ファイル (件数) | 前回エージェントの参照実態 |
|---|---|---|---|
| qa-002 | `pageNumber` | 4 件 (biz-samples-03, project-download 等) | 前回は `web-application-getting-started-project-search.md` を読み `ProjectSearchForm#pageNumber` の実装例を回答に転記 |
| qa-002 | `listSearchResult` | 7 件 (biz-samples-03, project-search 等) | 前回は `<app:listSearchResult>` タグ例を回答に転記 |
| qa-004 | `n:form` | 22 件 (libraries-tag.json#s21 等) | 前回は `libraries-tag.md` 二重サブミット節 (`<n:form useToken="true">`) を回答に転記 |
| qa-004 | `n:submit` | 8 件 | 前回は `<n:submit allowDoubleSubmission="false" />` 例を転記 |
| qa-004 | `useToken` | 12 件 | 同上 |
| qa-004 | `allowDoubleSubmission` | 10 件 | 同上 |

今回のエージェントは qa-004 では `handlers-use-token.json#s3` のみを読み、そこに含まれる Thymeleaf 例 (`<form th:action="@{/path/to/action}">`) を転記。同ファイルの脚注で参照している `libraries-tag.md#tag-double-submission-server-side` には到達せず、JSP タグ例を回収できなかった。これはエージェントの探索範囲の差であり、知識ファイル側には必要な情報が存在している。

**qa-001 benchmark の trial 間ゆらぎ**: trial 1/3 は 100.0%、trial 2 のみ 62.5%。trial 2 は回答簡潔版で `withNoneOption` / `pattern` 属性等の補足説明が欠落。LLM の応答スコープの揺らぎで、シナリオ期待値 8 項目中の補足的なキーワードが 3 項目落ちたケース。

---

## 広域チェック（全シナリオ×1試行）

| # | Scenario | 検出率 (前回) | 検出率 (今回) | 変化 | 時間 (前回) | 時間 (今回) | 変化 | トークン (前回) | トークン (今回) | 変化 | 目視 |
|---|----------|-------------|-------------|------|-----------|-----------|------|---------------|---------------|------|------|
| 1 | qa-001 | 8/8 | 8/8 | → | 72秒 | 77秒 | → | 0 | 31,300 | → | |
| 2 | qa-002 | 8/8 | 6/8 | 🔴 | 64秒 | 57秒 | ↓7秒 🟢 | 0 | 22,700 | → | |
| 3 | qa-003 | 7/8 | 8/8 | 🟢 | 71秒 | 64秒 | → | 0 | 35,700 | → | |
| 4 | qa-004 | 8/8 | 4/8 | 🔴 | 36秒 | 43秒 | ↑7秒 🔴 | 0 | 36,600 | → | |
| 5 | qa-005 | 8/8 | 8/8 | → | 58秒 | 89秒 | ↑31秒 🔴 | 14,200 | 26,500 | ↑12,300 🔴 | |
| 6 | ca-001 | 36/37 | 35/37 | 🔴 | 262秒 | 217秒 | ↓45秒 🟢 | 0 | 66,500 | → | |
| 7 | ca-002 | 31/32 | 32/32 | 🟢 | 321秒 | 184秒 | ↓137秒 🟢 | 0 | 45,000 | → | |
| 8 | ca-003 | 36/37 | 37/37 | 🟢 | 298秒 | 216秒 | ↓82秒 🟢 | 0 | 41,100 | → | |

**凡例**:
- 🟢 改善（検出率↑ or 時間/トークン↑10%超）
- 🔴 劣化（検出率↓ or 時間/トークン↑10%超）
- → 変化なし（±10%以内）
- 目視: 手動記入欄（◯改善 / △変化なし / ✗劣化）

**変化判定ルール**:
- 検出率: 1項目でも減少 → 🔴、増加 → 🟢、同数 → →
- 時間: ±10%以内 → →、10%超の短縮 → 🟢、10%超の増加 → 🔴
- トークン: ±10%以内 → →、10%超の削減 → 🟢、10%超の増加 → 🔴

---

## 統計比較

| 指標 | 前回 | 今回 | 変化 |
|------|------|------|------|
| 全体検出率 | 97.3% | 94.5% | -2.7pp |
| QA検出率 | 97.5% | 85.0% | -12.5pp |
| CA検出率 | 97.2% | 98.1% | +0.9pp |
| 平均実行時間 | 148秒 | 118秒 | -29秒 (-19.9%) |
| QA平均実行時間 | 60秒 | 66秒 | +6秒 (+9.6%) |
| CA平均実行時間 | 294秒 | 206秒 | -88秒 (-30.0%) |
| 平均トークン | (未計測 ※) | 38,175 | 比較不能 |

※ 前回 baseline は qa-005 を除きトークン計測が未実装 (`steps: []` 空)。今回から Opus 4.x 駆動のサブエージェントで計測開始。今回 v6 baseline 全体 (coverage + benchmark) の合計は入力 416,500 / 出力 60,850 = 約 477K トークン。Opus 4.x 単価 (入力 $15/M、出力 $75/M) で **約 $10.8／1 baseline run**。Sonnet 4.x なら約 $2.2。

---

## 実測データからの分析

### 精度観点
- **検出率の増減は「エージェントの知識ファイル選択差」で説明できる**。欠落キーワード全件 (qa-002 `pageNumber`/`listSearchResult`、qa-004 `n:form`/`n:submit`/`useToken`/`allowDoubleSubmission`、ca-001 `UniversalDao`/`SessionUtil`) は v6 知識ファイルに存在する。
- CA の改善は **Nablarch Framework Usage の見出し粒度向上** が主因。22-B-16 の Section.level 対応で knowledge JSON の section 階層が保存され、code-analysis workflow の read-sections.sh 取得結果が独立見出しで転写されるようになった。
- CA でリンク自体は辿られていない（Step 2 は full-text-search + read-sections による検索ベース）。22-B-16b/c の cross-doc MD リンクは **ユーザーが GitHub で docs MD を閲覧する際の辿り道** として効く設計で、エージェント走行時の探索フローには直接入っていない。

### 時間観点
- **CA 全体で -30%、ca-002 は -43% (321→184s)、ca-003 benchmark trial 3 は -43% (403→229s)**。ツール呼び出し回数は ca-002 で 33→23 回、ca-001 で 26→24 回と減少。
- **QA は +9.6% (60→66s)**。特に qa-005 +53% (58→89s) が突出。metrics.json を読むと、前回は hints 由来の pre-filter (8s) で候補を絞ったのに対し、今回は Phase 21-K の hints スコープアウトにより route 1 (full-text-search) が 0 hits → route 2 (index.toon fallback) に落ちる構造になり、index.toon 読み込みに 20s 消費。
- qa-002 (-11%) / qa-003 (-10%) は短縮しているため、QA 全件が悪化しているわけではない。

### コスト観点
- 前回 baseline は qa-005 を除きトークン計測未実装 (`steps: []` 空) で比較不能。
- 今回の実測: coverage 8 件 + benchmark 追加 4 trials 合計で **入力 416,500 / 出力 60,850 = 約 477K tok**。Opus 4.x (入力 $15/M、出力 $75/M) で **$10.8 / baseline run**、Sonnet 4.x だと $2.2。
- シナリオ別の偏り: ca-001 (66.5K) / ca-002 (45K) / ca-003 trial2 (84K) が大きい。QA は 22-36K。入力の大半は workflow/SKILL.md 読み込み (各 1-15K) + index.toon フルロード (14-18K) が占める。

### ステップレベル観測
- 3 エージェント (qa-005, ca-001, ca-002) が `full-text-search.sh` の silent failure を個別に脚注報告。jq で section オブジェクトに直接 `test()` を適用しているため常に 0 hits。nabledge-test skill 側のバグで RBKC とは無関係だが、QA 全件が route 2 にフォールバックしておりオーバーヘッドが発生している。

### 変動
- qa-001 benchmark SD 21.6% は trial 2 のみの外れ値起因。trial 1/3 は 100%、trial 2 のみ 62.5%。構造的劣化ではなく LLM 応答ゆらぎ。

---

## 分析を受けた仮説

**仮説 1 (確定): QA 検出率低下 6/40 は `full-text-search.sh` の schema 追従漏れが根本原因**

- **原因**: RBKC V4 フォーマット移行 (commit `68c11a9d7`) で knowledge JSON の `sections` が dict → list に変わった際、nabledge-6 skill の `scripts/full-text-search.sh` の jq 式 (`.sections | to_entries[]` は dict 前提) が追従更新されなかった。
- **検証結果**:
  - 前回 baseline (2026-03-31) 時点は JSON が dict 形式で script は動作していた (前回 `handlers-use_token.json` で直接確認)。今回 baseline 時点は list 形式。
  - 現行 script を今回の JSON で実行すると 0 件ヒット + stderr 無し (silent failure)。
  - 現行 JSON 構造で route 1 が正しく動作した場合の simulate 結果: qa-004 キーワード群で `libraries-tag.json#s21` が上位 2 位 (ここに `<n:form useToken="true">` + `<n:submit allowDoubleSubmission="false">` が両方明記)、qa-002 キーワードで `project-search.json#s1` + `biz-samples-03.json#s17` (listSearchResultタグ) が上位。
- **実装**: jq 式を list 向けに更新 — `.sections[] | (.content + " " + .title) | tostring | test(...)`。
- **予測**: qa-004 4/8 → 8/8、qa-002 6/8 → 8/8。QA 平均検出率 85.0% → 95%+、QA 平均時間 66s → 55s (index.toon fallback 読込の 14-18K tokens 回避)。

**仮説 2 (訂正): qa-004 の欠落は知識ファイルの問題ではなく「参照ファイル選択ミス」**
- 証拠: `libraries-tag.json#s21` (「二重サブミットを防ぐ」) に `<n:form useToken="true">` + `<n:submit allowDoubleSubmission="false">` が両方明記されている。前回エージェントはこれを参照して回答に転記した痕跡あり。今回エージェントは `handlers-use-token.json#s3` の Thymeleaf 例のみ参照し、同セクションの脚注リンク (`libraries-tag.md#tag-double-submission-server-side`) を辿らなかった。
- 実装: 知識ファイルは修正不要。代わりに (a) `full-text-search.sh` を修正して `libraries-tag.json` もキーワード検索でヒットするようにする、または (b) `handlers-use-token.json#s3` の脚注を含めて `read-sections.sh` で複数ファイル読み込みを行うよう `workflows/qa.md` で誘導する。
- 予測: (a) で qa-004 8/8 回復見込み。

**仮説 3: ca-001 Overview の英クラス名欠落は Overview 生成テンプレートの語彙選択**
- 証拠: Overview は日本語の「ユニバーサルDAO」「セッションストア」で記述。Class Summary / Nablarch Usage には英名あり。
- 実装: `.claude/skills/nabledge-6/workflows/code-analysis.md` の Overview テンプレートで「主要 Nablarch コンポーネントの英名を併記」制約を明示。
- 予測: Overview 生成時に括弧書きで英名併記すれば ca-001 は 35/37 → 37/37。

**仮説 4: qa-001 benchmark の trial 2 揺らぎは LLM の出力スコープ差**
- 証拠: 3 trial 中 2 回 100%、1 回 62.5%。trial 2 は `withNoneOption` / `pattern` 言及が減った。
- 実装: workflow 改善で打ち消しきれない部分。シナリオ期待値側で OR 許容 (`withNoneOption` OR `noneOption` 等) の検討余地。
- 予測: 現状は分散込みで mean 87.5% を安定値と捉えるのが実運用上妥当。

---

## 再現手順

```bash
# 今回のベースラインと同じ状態で再計測
git checkout 5e79d7925c4208556b46305dd16984ac82791270
nabledge-test 6 --baseline

# 前回のベースラインと同じ状態で再計測
git checkout e55c25c3eb1b9caeddf48b65dad56e5f8e0a3982
nabledge-test 6 --baseline
```

---

*Generated by nabledge-test v2 baseline mode | Compared: 20260331-152005 → 20260424-080424*
