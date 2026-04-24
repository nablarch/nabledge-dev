# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-24 (セクション単位 TF-IDF に方針転換、ゼロベースやり直し決定)

## ゴール (この PR の本質)

ids flow の L1 以下を 0 にする。Nabledge 品質基準 (1% リスク排除 / 品質は二値) に沿う。

## アプローチ: 段階分離

検索 → 回答 → 判定 の連鎖問題を一気に追うと原因が混線する。Phase 1 で検索だけを完成させ、その後 Phase 2 で回答に進む。

### Phase 1: 検索 LLM (AI-1) の精度向上 ← 今ここ

**目的**: a_fact の根拠 section が必ず selections に入る状態にする。

**2026-04-24 方針転換**: ページ単位 TF-IDF で allowlist 361 語を選定・配置した
結果、共通頻出語 (`バージョンアップ` / `@Published` / `後方互換` など) が特徴語
として浮上せず、review-10 系などの「知識はあるが見つからない」ケースを拾えない
ことが実データで判明。シミュレーションで **セクション単位 TF-IDF なら
これらが特徴語として出る** ことを確認 (例: `about-nablarch-versionup_policy|s4`
で `後方互換性 0.794` / `バージョンアップ 0.224` / `@Published 0.122`)。

前回の成果 (ページ単位 TF-IDF + 361 語 + 2898 配置) は **superseded として破棄**
し、セクション単位 TF-IDF ベースでゼロからやり直す。

**用語整理**: 「allowlist / 許可リスト」は実態 (候補抽出→自動分類→人間判定→採用
のキュレーション過程) と合わない表現。以後は **採用キーワード / INDEX_KEYWORDS_JA
/ index-keywords-ja.json** に統一。除外側の stoplist (JAVA_STOPLIST /
term_stopset) は真の block list なので stoplist のまま。

### Phase 2: 回答 LLM (AI-3) の改善 (Phase 1 完了後)

Phase 1 が 100% に届いたら着手。

## 検索フロー (今回の変更後の姿)

```
1. スクリプトが質問から term_queries を機械抽出
   - @Annotation, CamelCase, camelCase, カタカナ4+, 漢字4+
   - df_pct > 20% は grep 対象外

2. AI-1 が index-llm.md を読む
   - 各セクション行末に採用語が付いている
     例: `s3:制約 — スレッド / トランザクション管理`
   - AI-1 は selections のみ返す (term_queries 生成タスクは削除)

3. スクリプトが処理
   - term_queries を本文 grep
   - selections と grep ヒットを merge → read-sections

4. AI-3 が回答生成 (今回は変更しない)

5. judge (今回は走らせない、search-only モード)
```

## 今セッションまでの成果 (superseded)

### 既存コミット済・維持するもの

- [x] 検索フロー 2 経路の役割分担を確定
  - index-llm.md 経路: 日本語概念語で意味マッチ
  - term_queries 経路: ASCII 識別子 (4+ 字) で本文 grep
- [x] `tools/benchmark/docs/index-enrichment.md` 全体フロー記録 (**要修正: セクション単位に書き換え**)
- [x] `.claude/rules/benchmark.md` に「シミュレーションで手応え確認」追加
- [x] `setup.sh` に scikit-learn 追加
- [x] `term_extract.py` + tests + stopset 生成スクリプト (Step A、commit 済)
- [x] `search_ids.py` の AI-1 term_queries 廃止、prompts/search_ids.md 更新 (commit 済)

### 破棄するもの (superseded)

- [~] ページ単位 TF-IDF 人間判定結果 (.work/00307/manual-allowlist-ja-361.json / rounds/)
- [~] 現 index-llm.md (148 KB, 2898 配置) は上書きで再生成される
- [~] 現 build_index.py (ページ単位 allowlist 前提) は書き直す

## 次ステップ: セクション単位 TF-IDF でゼロベースやり直し

### Step 0: 用語・ドキュメントの整理

- [ ] allowlist → 採用キーワード / INDEX_KEYWORDS_JA にリネーム
  - `manual-allowlist-ja-*.json` → `index-keywords-ja.json`
  - `classify_terms.py` 内の `MANUAL_ALLOWLIST_JA` 定数名・注釈更新
  - `build_index.py` `--allowlist` → `--keywords`
- [ ] `docs/index-enrichment.md` をセクション単位 TF-IDF ベースに書き換え
  - 「ページ単位 TF-IDF を採用」→「セクション単位 TF-IDF を採用」
  - 配置ルール: セクションごとに独立計算、自セクションの上位語をそのセクション行末に配置
  - 人間判定の粒度: 「語 × セクション」単位で○/×
  - 旧 stop_title_overlap / page_body ロジックは不要化

### Step 1: classify_terms.py 書き直し

- [ ] 入力: (file_id, sid, body) のセクション列
- [ ] 出力: 「語 × セクション × スコア × top_sections (自セクション含む) × snippet」
- [ ] セクションごとに TF-IDF 上位 N 語を候補化 (例: 上位 20 語)
- [ ] JAVA_STOPLIST + term_queries パターン (@Annotation/CamelCase/camelCase) で除外
  - これらは term_queries 経路でカバー済、index には入れない
- [ ] 副産物ノイズ (利用者向 / アーキテクト向 など「他セクションに出ないだけ」語) の自動検出
  - 例: max_score < 0.10 は低信号として候補外に
- [ ] スコア帯別の pending バケット生成

### Step 2: 採用キーワード候補の人間判定 (ゼロから)

- [ ] 3 エージェント並列判定プロンプトをセクション単位向けに改訂
  - 入力に「語・セクションタイトル・セクション本文 snippet・スコア」を含める
  - (A)(B)(C) 基準: そのセクションの主題と結びついているか
- [ ] スコア帯別に段階判定 (ページ単位時と同じ分割粒度)
- [ ] 判定結果を `.work/00307/rounds-section-tfidf/` 以下に保存
- [ ] 最終採用キーワード: `.work/00307/index-keywords-ja.json` (語 × セクションのリスト)

### Step 3: build_index.py 書き直し

- [ ] 入力: セクション単位の採用キーワードリスト (語 × セクション)
- [ ] 採用キーワードが本文にヒットすることを再検証 (本来ヒットしない組は通さない)
- [ ] 配置: そのセクション行末にのみ配置 (同じ語が別セクションで採用されたら別々に配置)
- [ ] 失敗 / ヒットなしはエラー報告
- [ ] index-llm.md を再生成

### Step 4: 計測

- [ ] 失敗 9 件 + 成功 1 件 = 10 件 search-only
- [ ] `search_coverage.py` で coverage
- [ ] review-10 / impact-01 / review-05 など「ページ単位では拾えなかった」ケースが
      拾えるようになったかを検証
- [ ] 期待: review-10 で `about-nablarch-versionup_policy|s4/s5`, `about-nablarch-policy|s10/s12` が selections 候補に入る

### Step 5: 結果次第で判断

- 効果あり → 30 件フル search-only → Phase 2 へ
- 効果なし → セクション単位 TF-IDF の限界として整理、別経路 (embedding) を次 PR で検討

## Phase 2 (先送り、判断材料)

今回は AI-3 は変更しない。既知の課題は記録しておく:

- **over-reach**: C claim が多い。候補セクションから余計なトピックを拾って回答に混ぜる
- **C-claim 過剰**: 質問されていない注意点を埋める
- **under-reach**: s1 overview に寄りがちで、本体セクションを引用しない

Phase 2 で着手予定:
- [ ] AI-3 answer.md 改訂 (over-reach / under-reach 両面)
- [ ] PE レビュー + 実行ログ添付
- [ ] 30 件 rerun で L1 件数を測定
- [ ] judge の非決定性対策 (実測揺れが多ければ)

## やらないこと (スコープ外)

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (いたちごっこ、禁止)
- セクション単位 TF-IDF (今回はページ単位 TF-IDF + セクション配置)

## 方針確認済み

- 合格ライン = L2 以上。L1 は Nabledge 品質基準で失格
- 改善ターゲットは ids のみ
- 設計意図: AI-1 は recall 優先、AI-3 は precision 側で絞る
- 検索精度を上げるのに hints 調整はしない
- **変数を増やさない**: 今回の計測中は AI-3 は変更しない。原因切り分けのため

## 現在地の測定結果 (参考)

| 測定 | mean | L3 | L1 | 備考 |
|---|---|---|---|---|
| 旧 search + 旧 a_facts | 2.10 | 16 | 13+1 | 初回 30 件 |
| 旧 current | 2.17 | 18 | 11+1 | 比較用 |
| 旧 search + 新 a_facts (rejudge) | — | — | — | 8 件対象、judge 非決定性で不安定 |
| 新 search + 新 a_facts (30 件) | 2.20 | 18 | 12 | 4 件劣化 (C over-reach 混入) |
| 旧 index (既存) 30 件 search-only | — | — | — | ref 70% / expected 77% |
| **新 index 10 件 search-only** | — | — | — | **次セッションで測定** |

## Done (過去セッション)

- [x] search_ids.md を recall-first に書き直し (PE review 4/5 approve、M1/M2 反映)
- [x] a_facts 横並びチェック (30 件) → 8 件修正 (5 削除 / 4 追加)
- [x] 新 search + 新 a_facts で 30 件再計測 → mean=2.20, L3=18, L1=12
- [x] L1 12 件の検索 vs 回答 切り分け → 検索 OK 9 件 / 検索漏れ 3 件
- [x] 検索漏れ 3 件の LLM 思考ログ確認 → 「質問を狭く解釈」が共通原因
- [x] term 検索シミュレーション → 固有名は ~1 ヒットで精度高い、概念語は誤爆
- [x] term_queries 実装 + PE review (`960bfef3f`, `d4316f851`)
- [x] search-only mode + coverage 測定ツール (`9baf22051`)
- [x] 30 件 search-only 実測 (ref coverage 70%)
- [x] ファイル未選択 4 件のサブエージェント自由 grep 実験
- [x] a_fact 代替経路の直接 grep 確認 (3/4 件は模範回答 citation 唯一解ではない)

## 既知の bug / 対処済

- judge tool_use 壊れた input → `_is_well_formed_tool_input` フィルタで除外
- max_turns 2 で A 長いと切れる → 4 に引き上げ
- `list(string)` で char-list 化する事故 → `_facts()` type ガード

## 初期タスク群 (完了済)

- [x] 30 シナリオ + 模範回答 30件作成
- [x] 2-flow 比較基盤 (ids / current)
- [x] Haiku vs Sonnet 比較 → Sonnet 固定
- [x] 30件 × 2 flow 初回計測
- [x] AI-3 answer プロンプト改訂 (Use only what you need, PE レビュー反映済み)
- [x] `.claude/rules/benchmark.md` 新設 (並列実行禁止ルール)
- [x] 試行錯誤削除 / ベンチマークツール全面リファクタ (1572 → 1130行)
- [x] notes.md を設計判断のみに整理
- [x] baseline を新レイアウトに変換 / 全テスト 19件 GREEN
- [x] answer.md 改訂で ids 30件再計測
- [x] current variant は旧 baseline 流用と判断 (answer.md 非依存を確認)
- [x] `.claude/rules/development.md` 追記 (実出力目視・レビューに実行ログ添付)
- [x] judge 方式確定: A 事前準備 / B,C は KB (ref∪retrieved) 基準
- [x] scenarios JSON に `a_facts` フィールド追加、io/types/judge.py 改修
- [x] 30 scenario に A-fact を書いた (手書き 1 + Agent 草案 29 → 17件は私がレビュー修正)
