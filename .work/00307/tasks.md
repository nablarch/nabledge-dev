# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-27 (H-1 完了 `22d866850`、次は H-2)

## ゴール

ids flow の L1 以下を 0 にする (Nabledge 品質基準: 1% リスク排除 / 品質は二値)。

## アプローチ

検索 → 回答 の連鎖問題を一気に追うと原因が混線する。まず **検索** (Phase 1) を完成させ、次に **回答** (Phase 2) を改善する。**Phase 2 は必須**、検索だけでは L1=0 到達不可。

## 検索フロー (改善後)

```
1. スクリプトが質問から term_queries を機械抽出 (ASCII 4+ のみ)
2. AI-1 が index-llm.md を読む (各セクション行末に採用キーワードが付いている)
3. term_queries を本文 grep、AI-1 selections と merge → read-sections
4. AI-3 が回答生成
5. judge
```

## 進捗

### 完了 (Phase 1 準備)

- [x] **Step 0**: `docs/index-enrichment.md` 書き換え — `93af2c75d`
- [x] **Step 1**: stoplist 確定 (51 語) — `254816140` + `8959cb76d`
  - `section_df_ja.py` 新規 (TDD 18 テスト GREEN)
  - section_df ≥ 100 全員 stoplist / 50-99 で 19/31 / 30-49 で 18/43 / <30 全員残す
  - 判定過程: `stoplist-judgment.md`
- [x] **パラメータ凍結** — `ed115b132`
  - 採用語: tf≥2 で上位 5、候補 0 なら fallback tf=1 df≤20 で上位 3
  - 凍結根拠: `index-params-decision.md` (コーパス統計のみで決定、出来レース回避)
- [x] **10 件シミュレーション** — L1 検索漏れ 10 件で効果を LLM 視点で判定
  - 決定的 3 件 (impact-07, impact-03, req-05)
  - 確度上がる 5 件 (impact-01, req-04, review-08, impact-10, review-01)
  - 効果薄 2 件 (impact-08, req-10)

### Phase 1 残タスク

#### Step 2: classify_terms.py 書き直し (セクション単位 TF) ✅

- [x] 入力: knowledge JSON + stoplist
- [x] 各セクションで tokenize → TF 計算 → stoplist / ページ・セクションタイトル重複除外
  - 識別子パターンは日本語 tokenizer が 4+ 字 JP のみを拾うため明示除外不要
- [x] tf≥2 上位 5 語、候補 0 なら fallback tf=1 df≤20 で上位 3 語
- [x] 出力: `tools/benchmark/data/index-keywords-ja.json` — 生成済 (`c75a99c71`)
- [x] 既存 `classify_terms.py` のページ単位 TF-IDF ロジックを完全置き換え
- [x] TDD: `tests/test_classify_terms.py` 書き直し (22 tests GREEN)

#### Step 3: build_index.py 書き直し ✅

- [x] 入力: `--allowlist` → `--keywords`、`index-keywords-ja.json` を読む
- [x] 各セクション行末に ` — keyword / keyword / ...` 形式で付記
- [x] index-llm.md 生成 — 1411 sections / 3196 placements (`c75a99c71`)
- [x] TDD: `tests/test_build_index.py` 更新 (10 tests GREEN)

#### Step 4: 初回計測 (完了、悪化 3 件判明)

- [x] 10 件 search-only 実施 (`$4.10`, 4 分)
- [x] `search_coverage.py` で旧 vs 新 index 比較
- [x] 結果: expected_full 3/10 → 5/10、ref_full 2/10 → 4/10 (ネット改善)
- [x] ただし **悪化 3 件** 判明:
  - `req-05`: satisficing。`libraries-message` で満足し `libraries-code|s3` (タイトルに「多言語化」) を取らず
  - `review-01 s2`: タイトル「リクエストパス指定」だが本文は DataReader カタログ → title のみでは救えない
  - `review-08 s8`: タイトル「例外振る舞い」だが本文に DBCM ハンドラ/排他に直結 → title のみでは救えない
- [x] パラメータは動かさない (凍結維持、出来レース回避)
- [x] エキスパート再評価: 2/3 が Read 必須 → **4 ステップ Read 方式へ pivot**

#### Step 5: 4 ステップ Read-based AI-1 実装 (新規・最優先)

**設計合意 (`.work/00307/review-by-prompt-engineer-*` 系 PE 相談で確定)**:

- 4 ステップ手続き:
  1. intent 抽出 (質問から内容語と意図)
  2. index sweep → ファイル単位で候補列挙
  3. 各候補を Read → セクション本文で判断、evidence 引用
  4. 最終セクション選定 (10-15)
- `allowed_tools=["Read"]`、knowledge ディレクトリ限定
- `max_turns=8`
- schema は `intent` / `candidate_files` / `read_notes` / `selections` を全部返す
- evidence は **verbatim substring** (本文コピペ) 必須、事後に部分文字列一致検証
- `selections[].matched_on` enum (`title`/`keyword`/`body`) で分析用シグナル

**合格基準** (`review-by-prompt-engineer-*` 最新):
- 全体精度 ≥ baseline
- `review-01 s2` / `mth s8` 回復
- evidence 不一致率 ≤ 5%
- schema 検証失敗 ≤ 2%
- 中央値 wall time が 2 倍以内

**実装タスク (完了)**:
- [x] `build_index.py`: index-llm.md のヘッダ行にファイルパス埋め込み (`26f0af9a0`)
- [x] `search_ids.py`: `allowed_tools=["Read"]`、`max_turns=10`、evidence 事後検証
  - evidence 検証は Read-attestation 方針: verbatim / 正規化 / 30 字 prefix のいずれか
- [x] `prompts/search_ids.md`: 4 ステップ手続き型 + Step 5 回答生成マージ
- [x] schema 差し替え (intent/candidate_files/read_notes/selections/conclusion/evidence/caveats/cited)
- [x] AI-1 + AI-3 をマージ (回答もこの 1 コールで返す)
- [x] 呼び出し側で Markdown レンダリング (ファイル保存は caller 責務)
- [x] benchmark ツール全体を `--version` 対応 (v5/v1.x も共通経路で実行可, `301178566`)
- [x] judge に KB 検証追加: Grep/Read で C-claim を KB 全体で確認
- [x] judge 新 reason `SUPPORTED_BY_KB` (減点なし) + `kb_evidence.quote` verbatim 検証 (`36ae333ba`)
- [x] judge `max_turns=15` / `timeout=420` / 予算 10 tool call ルール (`72f62aa88`)
- [x] 1 件試走 (req-05): $0.83 / 110 秒
- [x] 3 件試走 (req-05/review-01/review-08, merged + KB-verify judge):
  - req-05: L3 (完全)
  - review-01: L3 (judge 側 SUPPORTED_BY_KB で救済、旧 L1)
  - review-08: L1 のまま (AI-1 が mth|s8 を selections に入れたが evidence で cite せず、A-fact 4 MISSING)
  - mean_level: 2.33, cost $3.64

**合格基準**:
- [x] `review-01 s2` 回復
- [x] evidence 不一致率 ≤ 5% (緩和後はほぼ 0%)
- [x] schema 検証失敗 ≤ 2%
- [ ] `mth s8` 回復 ← **Step 6 で対応**
- [ ] 10 件で安定 7 件が回帰しないこと
- [ ] 30 件での mean_level 計測

**コスト実績**:
- 現状: $0.40/Q × 30 = $12/run
- Read + マージ: 平均 $1.09/Q × 30 ≈ $32/run (3 件平均 $1.21)

#### Step 6: search_ids.md プロンプト品質改善 (最優先)

**根本原因の特定 (2026-04-27)**:
- AI-1 が Read を1回も呼ばずに StructuredOutput を直接返していた（stream ログ確認済み）
- s5 はそもそも selections に入っていなかった（tasks.md の旧認識「s8 選定済みで evidence に入れず」は誤り）
- 質問が純粋日本語のため grep_term_hits もゼロヒット

**確認された課題 4点**:
1. プロンプトのベストプラクティス違反 — ステップが肯定文の明確な命令になっていない。AIが迷わず実行できる状態でない
2. 候補ファイル全量 Read → セクション選定 → 回答生成の徹底不足 — Read を強制する設計になっておらず、インデックスだけ見て返すことが許容されている
3. 出来レース的ルールの混入 — Step 4 の「`制約`/`前提`/`ハンドラ配置` も含めよ」はハンドラ構造前提で削除すべき
4. 各ステップの結果・判断理由がスキーマに記録されない — 性能改善に必要な情報が取れていない

**作業ステップ**:
- [x] search_ids.md を4点の課題に沿って書き直す（実行ログ取得済み）
  - Read 強制 ("MANDATORY" + structural requirement)、「制約/前提/ハンドラ配置」削除、命令形明確化
  - `files_read_count` フィールド追加（診断用）
  - evidence 上限: 200→500 chars、「≤500 なら全文コピー」指示
  - caveats を section 本文根拠必須に強化
  - evidence maxItems: 8→10（スロット圧対策）
  - scope check 指示追加（multi-process文脈の誤適用防止）
  - search_ids.py: timeout 300→420s、schema 更新
- [ ] review-08 を **3 回連続 L3** にする（現状: L3/L1/L1/L1/L1 = 1/5）
  - **原因分析済み**:
    - s8 evidence が切り取られる問題 → evidence full-body コピー指示で改善傾向
    - C-claim hallucination: caveats に KB 未確認事実を追加する問題 → 「section 本文根拠必須」で対処中
    - multi-process セクション誤適用 → scope check 指示追加で対処中
  - **最新状態**: `caveats MUST be grounded` 指示を追加した版（コミット未）で試走中断
  - [x] DECISION 解消 — PE エキスパートレビュー実施 (2026-04-27)、H1〜L2 の 9 件修正を全対応する方針をユーザーが承認
- [x] **H-1**: `caveats` schema を `{note, cited}[]` に変更 (search_ids.py + テスト + プロンプト) — `22d866850`
- [ ] **H-2**: scope_note を Step 3 (read_notes) へ前出し (search_ids.py schema + プロンプト)
- [ ] **H-3**: 自己検証サブステップ追加 (プロンプトのみ)
- [ ] **M-1**: 候補ファイル上限 20→12 (search_ids.py schema maxItems + プロンプト)
- [ ] **M-2**: precision 優先の明示 (プロンプトのみ)
- [ ] **M-3**: Step 3 内部表記 `evidence` → `body_excerpt` (プロンプトのみ)
- [ ] **M-4**: 実行モデル明確化 (プロンプトのみ)
- [ ] **L-1**: matched_on タイブレーク追記 (プロンプトのみ)
- [ ] **L-2**: Read エラー処理 (search_ids.py schema + プロンプト)
- [ ] PE レビューファイル保存 (`.work/00307/review-by-prompt-engineer-step6-h1l2.md`)
- [ ] 3 件試走（req-05 / review-01 / review-08）で効果測定
- [ ] 結果が 3 件 mean ≥ 2.33 かつ review-08 L3 なら次へ

#### Step 6: 検索が安定したら回答統合の検討 (条件付き次期)

検索が安定して evidence も取れているなら、**本文は既に読んでいる**。
AI-3 を別呼び出しにせず、AI-1 に回答生成まで含める案を検討。

- [ ] 安定後、AI-1 プロンプトに回答生成ステップ追加を評価
- [ ] ファイル出力 (answer.md / search.json 等) は**呼び出し側のスクリプト**で実施 (AI-1 は JSON 返却のみ)
- [ ] 呼び出し側分離の意図: AI-1 の責務を「探す+答える」に閉じ、保存形式は外で決める

#### Step 7: 結論と Phase 2 移行

- [ ] 結果を文書化
- [ ] 検索改善が十分 or 不十分でも Phase 2 へ進む

### Phase 2 (必須): AI-3 回答プロンプト改善

L1=0 到達には検索改善だけでは不十分。`l1-root-cause-analysis.md` で既に特定済の AI-3 側の問題を解消する。

**既知の課題**:
- **over-reach**: 候補セクションから余計なトピックを拾う (C claim 過剰)
- **under-reach**: s1 overview に寄って本体セクションを引用しない
- **主役誤認**: 複数ハンドラ retrieved 時の主役取り違え (impact-10 など)

**タスク**:
- [ ] AI-3 `answer.md` 改訂
- [ ] PE レビュー + 実行ログ添付 (`.claude/rules/development.md`)
- [ ] 30 件 rerun で L1 件数測定
- [ ] judge 非決定性対策 (揺れが多ければ)

## 測定結果 (参考)

| 測定 | mean | L3 | L1 | 備考 |
|---|---|---|---|---|
| 旧 search + 旧 a_facts | 2.10 | 16 | 13+1 | 初回 30 件 |
| 旧 current | 2.17 | 18 | 11+1 | 比較用 |
| 新 search + 新 a_facts (30 件) | 2.20 | 18 | 12 | 前回 baseline |
| 新 index 10 件 search-only | — | — | — | exp_full 3/10→5/10, ref_full 2/10→4/10、悪化 3 件 (req-05/review-01 s2/mth s8) |
| 4-step Read AI-1 merged 3 件 | 2.33 | — | 1 | req-05 L3 / review-01 L3 / review-08 L1 ($3.64) |
| (trial4 aspects 追加) | 1.67 | — | 2 | **revert 済** — req-05 L0 / review-01 L3 / review-08 L1 |
| Step 6 改訂版 単件 | — | — | — | review-08: L3(1)/L1(4) — search は機能、answer 生成の C-claim/MISSING が原因 |
| Step 6 改訂版 (今日) review-01 | 1.0 | 0 | 1 | C-claim hallucination (KB未裏付け "INSERT前TRUNCATE設計") |
| Step 6 改訂版 (今日) req-05 | 1.0 | 0 | 1 | C-claim hallucination (ThreadContext自動取得 → libraries-code:s3 曲解) |

## スコープ外

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (出来レース禁止)

## 方針確認済み

- 合格ライン = L2 以上
- 改善ターゲットは ids のみ
- AI-1 recall 優先、AI-3 precision 側で絞る
- hints 調整はしない (出来レース禁止)
- 変数を増やさない (計測中は AI-3 を変更しない、Phase 2 で独立改善)
